#!/usr/bin/env node
import fs from "node:fs/promises";
import process from "node:process";

const args = new Map();
for (let index = 2; index < process.argv.length; index += 2) {
  args.set(process.argv[index], process.argv[index + 1]);
}

const companiesPath = args.get("--companies");
const planPath = args.get("--plan");
if (!companiesPath || !planPath) {
  console.error("Usage: node validate_itinerary_plan.mjs --companies companies.json --plan plan.json");
  process.exit(2);
}

const companies = JSON.parse(await fs.readFile(companiesPath, "utf8"));
const plan = JSON.parse(await fs.readFile(planPath, "utf8"));
const errors = [];

const parseTime = (value, field) => {
  const match = /^(\d{2}):(\d{2})$/.exec(String(value));
  if (!match) {
    errors.push(`${field} must use HH:MM`);
    return 0;
  }
  const hours = Number(match[1]);
  const minutes = Number(match[2]);
  if (hours > 23 || minutes > 59) errors.push(`${field} is not a valid time`);
  return hours * 60 + minutes;
};

if (!Array.isArray(companies) || companies.length === 0) errors.push("companies.json must be a non-empty array");
if (!Array.isArray(plan.days) || plan.days.length === 0) errors.push("plan.days must be a non-empty array");

const companyIds = companies.map((company) => String(company.id));
const duplicateCompanyIds = companyIds.filter((id, index) => companyIds.indexOf(id) !== index);
if (duplicateCompanyIds.length) errors.push(`Duplicate company IDs: ${[...new Set(duplicateCompanyIds)].join(", ")}`);

const startMinutes = parseTime(plan.workdayStart, "workdayStart");
const endMinutes = parseTime(plan.workdayEnd, "workdayEnd");
const mode = plan.mode ?? "all";
const maxDays = plan.maxDays == null ? null : Number(plan.maxDays);
const visitMinutes = Number(plan.visitMinutes);
const lunchMinutes = Number(plan.lunchMinutes ?? 0);
const lunchAfterStop = Number(plan.lunchAfterStop ?? 0);
if (!(endMinutes > startMinutes)) errors.push("workdayEnd must be after workdayStart");
if (!String(plan.startLocation ?? "").trim()) errors.push("startLocation is required");
if (!["all", "limited"].includes(mode)) errors.push('mode must be "all" or "limited"');
if (mode === "limited" && (!Number.isInteger(maxDays) || maxDays <= 0)) errors.push("limited mode requires a positive integer maxDays");
if (mode === "limited" && Array.isArray(plan.days) && plan.days.length > maxDays) errors.push(`Plan uses ${plan.days.length} days, exceeding maxDays ${maxDays}`);
if (!(visitMinutes > 0)) errors.push("visitMinutes must be positive");
if (!(lunchMinutes >= 0)) errors.push("lunchMinutes must be non-negative");

const scheduledIds = [];
const daySummaries = [];
for (const [dayIndex, day] of (plan.days ?? []).entries()) {
  if (!Array.isArray(day.stops) || day.stops.length === 0) {
    errors.push(`Day ${day.day ?? dayIndex + 1} has no stops`);
    continue;
  }
  const startTravel = Number(day.startTravelMinutes ?? 0);
  const returnTravel = Number(day.returnTravelMinutes ?? 0);
  if (!Number.isFinite(startTravel) || startTravel < 0) errors.push(`Day ${day.day}: invalid startTravelMinutes`);
  if (!Number.isFinite(returnTravel) || returnTravel < 0) errors.push(`Day ${day.day}: invalid returnTravelMinutes`);
  if (!plan.returnToStart && returnTravel !== 0) errors.push(`Day ${day.day}: returnTravelMinutes must be 0 when returnToStart is false`);
  let cursor = startMinutes + (Number.isFinite(startTravel) ? startTravel : 0);
  for (const [stopIndex, stop] of day.stops.entries()) {
    const id = String(stop.id);
    scheduledIds.push(id);
    const travel = Number(stop.travelFromPreviousMinutes);
    if (!Number.isFinite(travel) || travel < 0) errors.push(`Day ${day.day}: stop ${stopIndex + 1} has invalid travel minutes`);
    if (stopIndex === 0 && travel !== 0) errors.push(`Day ${day.day}: first stop travel must be 0`);
    if (stopIndex > 0) cursor += Number.isFinite(travel) ? travel : 0;
    if (stopIndex === lunchAfterStop && lunchAfterStop > 0) cursor += lunchMinutes;
    const visitStart = cursor;
    cursor += visitMinutes;
    if (cursor > endMinutes) errors.push(`Day ${day.day}: stop ${stopIndex + 1} ends after workdayEnd`);
    if (visitStart < startMinutes) errors.push(`Day ${day.day}: stop ${stopIndex + 1} starts before workdayStart`);
  }
  if (plan.returnToStart) cursor += Number.isFinite(returnTravel) ? returnTravel : 0;
  if (cursor > endMinutes) errors.push(`Day ${day.day}: route finishes after workdayEnd`);
  daySummaries.push({
    day: day.day ?? dayIndex + 1,
    stops: day.stops.length,
    startTravelMinutes: startTravel,
    returnTravelMinutes: plan.returnToStart ? returnTravel : 0,
    finish: `${String(Math.floor(cursor / 60)).padStart(2, "0")}:${String(cursor % 60).padStart(2, "0")}`,
    bufferMinutes: endMinutes - cursor,
  });
}

const companySet = new Set(companyIds);
const scheduledSet = new Set(scheduledIds);
const missing = companyIds.filter((id) => !scheduledSet.has(id));
const unknown = scheduledIds.filter((id) => !companySet.has(id));
const duplicateScheduled = scheduledIds.filter((id, index) => scheduledIds.indexOf(id) !== index);
if (unknown.length) errors.push(`Unknown company IDs: ${[...new Set(unknown)].join(", ")}`);
if (duplicateScheduled.length) errors.push(`Scheduled more than once: ${[...new Set(duplicateScheduled)].join(", ")}`);

const unscheduled = Array.isArray(plan.unscheduled) ? plan.unscheduled : [];
const unscheduledIds = unscheduled.map((item) => String(item.id));
const unscheduledSet = new Set(unscheduledIds);
const duplicateUnscheduled = unscheduledIds.filter((id, index) => unscheduledIds.indexOf(id) !== index);
const unknownUnscheduled = unscheduledIds.filter((id) => !companySet.has(id));
const overlap = unscheduledIds.filter((id) => scheduledSet.has(id));
const unaccounted = companyIds.filter((id) => !scheduledSet.has(id) && !unscheduledSet.has(id));
if (duplicateUnscheduled.length) errors.push(`Unscheduled more than once: ${[...new Set(duplicateUnscheduled)].join(", ")}`);
if (unknownUnscheduled.length) errors.push(`Unknown unscheduled IDs: ${[...new Set(unknownUnscheduled)].join(", ")}`);
if (overlap.length) errors.push(`IDs are both scheduled and unscheduled: ${[...new Set(overlap)].join(", ")}`);
if (unscheduled.some((item) => !String(item.reason ?? "").trim())) errors.push("Every unscheduled company requires a reason");
if (mode === "all") {
  if (missing.length) errors.push(`Missing company IDs: ${[...new Set(missing)].join(", ")}`);
  if (unscheduledIds.length) errors.push("all mode cannot contain unscheduled companies");
} else if (unaccounted.length) {
  errors.push(`Companies are neither scheduled nor unscheduled: ${[...new Set(unaccounted)].join(", ")}`);
}

const result = {
  valid: errors.length === 0,
  mode,
  maxDays,
  companies: companyIds.length,
  scheduledStops: scheduledIds.length,
  unscheduledCompanies: unscheduledIds.length,
  days: daySummaries.length,
  minimumBufferMinutes: daySummaries.length ? Math.min(...daySummaries.map((day) => day.bufferMinutes)) : null,
  daySummaries,
  errors,
};
console.log(JSON.stringify(result, null, 2));
if (errors.length) process.exit(1);
