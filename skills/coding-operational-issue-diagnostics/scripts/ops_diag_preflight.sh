#!/usr/bin/env bash
set -u

namespace=""
resource_group=""
static_web_app=""
all_namespaces="false"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --namespace)
      namespace="${2:-}"
      shift 2
      ;;
    --resource-group)
      resource_group="${2:-}"
      shift 2
      ;;
    --static-web-app)
      static_web_app="${2:-}"
      shift 2
      ;;
    --all-namespaces)
      all_namespaces="true"
      shift
      ;;
    -h|--help)
      cat <<'USAGE'
Usage: ops_diag_preflight.sh [--namespace NAME] [--resource-group NAME]
                             [--static-web-app NAME] [--all-namespaces]

Runs read-only local, PostgreSQL, Docker, Azure CLI, and kubectl checks. Output
may include subscription IDs, resource names, pod names, and log snippets, but
it avoids secret-oriented commands.
USAGE
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

section() {
  printf '\n## %s\n' "$1"
}

run() {
  local label="$1"
  local command="$2"
  section "$label"
  if command -v timeout >/dev/null 2>&1; then
    timeout 25s bash -lc "$command" 2>&1 || true
  else
    bash -lc "$command" 2>&1 || true
  fi
}

have() {
  command -v "$1" >/dev/null 2>&1
}

run "Host context" "date -u && pwd && git status --short 2>/dev/null || true"

if have python; then
  run "Python" "python --version && which python && python -m pip --version 2>/dev/null"
fi

postgres_found="false"

if have psql; then
  postgres_found="true"
  run "PostgreSQL client" "psql --version"
  psql_cmd="psql -X -v ON_ERROR_STOP=1 -d \"\${PGDATABASE:-postgres}\" "
  psql_cmd="${psql_cmd}-c 'select current_database(), current_user, now();'"
  run "PostgreSQL local metadata query" "$psql_cmd"
fi

if have pg_isready; then
  postgres_found="true"
  run "PostgreSQL readiness" "pg_isready"
fi

if [ "$postgres_found" = "false" ]; then
  section "PostgreSQL"
  echo "psql and pg_isready not found"
fi

if have docker; then
  docker_cmd="docker version --format '{{.Client.Version}}' && "
  docker_cmd="${docker_cmd}docker ps --all "
  docker_cmd="${docker_cmd}--format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'"
  run "Docker" "$docker_cmd"
fi

if have az; then
  account_query="{name:name, subscriptionId:id, user:user.name, tenantId:tenantId}"
  run "Azure account" "az account show --query '$account_query' -o table"
  if [ -n "$resource_group" ]; then
    group_query="{name:name, location:location, provisioningState:properties.provisioningState}"
    group_cmd="az group show -n '$resource_group' --query '$group_query' -o table"
    run "Azure resource group" "$group_cmd"
  fi
  if [ -n "$resource_group" ] && [ -n "$static_web_app" ]; then
    swa_query="{name:name, defaultHostname:defaultHostname, branch:branch, sku:sku.name}"
    swa_cmd="az staticwebapp show -g '$resource_group' -n '$static_web_app'"
    swa_cmd="${swa_cmd} --query '$swa_query' -o table"
    run "Azure Static Web App" "$swa_cmd"

    env_cmd="az staticwebapp environment list -g '$resource_group'"
    env_cmd="${env_cmd} -n '$static_web_app' -o table"
    run "Static Web App environments" "$env_cmd"
  fi
else
  section "Azure CLI"
  echo "az not found"
fi

if have kubectl; then
  run "Kubernetes context" "kubectl config current-context && kubectl cluster-info"
  run "Kubernetes nodes" "kubectl get nodes -o wide"
  if [ "$all_namespaces" = "true" ]; then
    run "Kubernetes pods" "kubectl get pods -A -o wide"
    run "Kubernetes recent events" "kubectl get events -A --sort-by=.lastTimestamp | tail -50"
  elif [ -n "$namespace" ]; then
    ns_cmd="kubectl get deploy,rs,pod,svc,ingress -n '$namespace' -o wide"
    run "Kubernetes namespace resources" "$ns_cmd"

    events_cmd="kubectl get events -n '$namespace' --sort-by=.lastTimestamp | tail -50"
    run "Kubernetes namespace events" "$events_cmd"
  else
    run "Kubernetes namespaces" "kubectl get ns"
  fi
else
  section "kubectl"
  echo "kubectl not found"
fi
