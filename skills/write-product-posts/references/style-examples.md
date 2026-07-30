# Product-post voice reference

This reference distills recurring patterns from public Zornade LinkedIn posts reviewed on 30 July 2026. Use it to reproduce the editorial mechanics, not to reuse Zornade-specific facts or copy its wording.

## Voice fingerprint

- Sound like the person who built the feature and knows why it exists.
- Start from an actual inconvenience, not a promotional claim.
- Move easily between implementation detail and user consequence.
- Earn trust with exact data, named sources, validation, or candid limitations.
- Prefer an understated “we fixed this” to a launch announcement.
- Use colloquial Italian without turning the post into a comedy sketch.
- Let related sentences stay together and flow as prose; paragraph breaks should mark an actual turn in the thought.
- Let open source, affordability, and dislike of badly made systems appear as convictions rather than slogans.
- Keep the company voice close to the founder voice.

Short source fragments that show the cadence include “un click, bam”, “Che pace”, “trictracbum”, “Aggratis”, and “A me il frontend non mi piace”. Treat these as evidence of rhythm; do not repeat them by default.

## Recurring source-derived patterns

### Interface cleanup

Observed story:

- A list of saved cadastral parcels had become a dense grid of numbers.
- The update replaced the grid with the parcel's silhouette and essential information.
- Full details remained available on the detail page.
- The list also became lighter because it stopped fetching unnecessary data.
- The post ended with a mundane analogy about the relief of removing background noise.

Lesson: explain visual cleanup as both a usability improvement and a technical improvement, then close on the feeling it creates.

### Better geographic data

Observed story:

- Italy used detailed borders while the rest of the world used a visibly rougher source.
- The mismatch became obvious while zooming.
- A higher-resolution global source increased the available elements from 177 to 242.
- The post closed with self-deprecating frustration about poor frontend work.

Lesson: make the defect visible, state exactly what changed, quantify it, and allow one opinionated line.

### Evidence with honest limits

Observed story:

- Active-fire alerts were added to the map and saved parcels.
- The source was identified as NASA VIIRS data.
- Validation against an official European system found 70.7% coverage overall and 79.3% for fires larger than ten hectares.
- Missed cases were explained through satellite limits such as clouds, short duration, and small fires.

Lesson: a limitation can strengthen the post. Report what the system catches, what it misses, and why.

### Reduce a difficult workflow

Observed story:

- Finding a cadastral parcel normally meant dealing with fragmented portals and obscure codes.
- The new search followed Region → Province → Municipality → Sheet → Parcel.
- Each selection filtered the next one and moved the map.
- The benefit was summarized as reaching one parcel among tens of millions in five clicks.

Lesson: when the workflow is the feature, show the sequence and contrast it with the old cognitive load.

### Launch without launch language

Observed story:

- A mapping tool was introduced as a second place to use the product.
- Its value was explained through a recognizable outcome: editorial maps without needing to know GeoJSON.
- Real data sources and several map types made the capability tangible.
- The motivation was framed as an honest alternative between expensive subscriptions, closed systems, and complex desktop software.

Lesson: define the product through what someone can now make, then explain why the builder wanted it to exist.

### Recognition and user participation

Observed stories:

- External approval was announced in one compact sentence rather than a press release.
- A calculator suggested by one user became a public thank-you and a small product story.

Lesson: keep recognition short. For user-inspired work, name the conversation and show that users participate in engineering decisions.

## Complete paired examples

These examples are rewritten from the observed story patterns. They demonstrate structure and adaptation; they are not verbatim copies.

### Example 1: interface and performance

#### Italiano

Le card delle particelle salvate stavano cercando di fare troppe cose insieme: forma, codici, superfici, valori, tutto dentro una lista. Adesso mostrano la sagoma reale della particella e le informazioni che servono per riconoscerla; il resto non è sparito, è nella scheda di dettaglio dove c'è abbastanza spazio per leggerlo.

In più la lista non scarica dati che non deve ancora mostrare, quindi si apre più leggera. Ci sono meno numeri davanti agli occhi e meno numeri che viaggiano inutilmente, che non è male per una modifica nata soprattutto per fare un po' d'ordine.

#### English

The saved-parcel cards were trying to do too much at once: shape, identifiers, area, values, all squeezed into a list. They now show the parcel's actual outline and the few details needed to recognize it, while the rest lives on the detail page where there is room to read it properly.

The list also stopped downloading data it does not need yet, so it loads faster. What started as a visual cleanup ended up removing some pointless work for the browser too, which seems like a fair outcome.

### Example 2: measured capability

#### Italiano

Da qualche giorno la mappa segnala gli incendi attivi vicino alle particelle salvate. Il dato arriva dai satelliti VIIRS ed è aggiornato più volte al giorno; prima di pubblicarlo lo abbiamo confrontato con il sistema europeo e abbiamo visto che intercetta il 70,7% degli incendi registrati nell'ultimo anno, percentuale che sale al 79,3% per quelli sopra i dieci ettari.

Il resto non scompare per magia: gli incendi piccoli, brevi o coperti dalle nuvole possono sfuggire al passaggio del satellite. Non è un oracolo e non va trattato come tale, ma aggiunge un segnale utile nel posto in cui serve.

#### English

The map now flags active fires near saved parcels using VIIRS satellite data refreshed several times a day. Before shipping it, we compared the results with the European reference system: it detected 70.7% of recorded fires from the past year, rising to 79.3% for fires larger than ten hectares.

Small, short-lived, or cloud-covered fires can still be missed because that is a physical limit of the observation method, not a percentage to hide in a footnote. The feature is not an oracle, but it adds one useful signal where it matters.

### Example 3: workflow improvement

#### Italiano

Per trovare una particella non serve più ricordarsi i codici catastali o saltare tra tre portali. Si sceglie la regione, poi la provincia, il comune, il foglio e la particella; ogni passaggio filtra quello successivo e porta la mappa nel posto giusto.

Sono cinque scelte comprensibili per arrivare a un elemento preciso in mezzo a milioni. Ogni tanto la tecnologia può anche togliere lavoro invece di aggiungerlo.

#### English

Finding a cadastral parcel no longer requires memorizing administrative codes or bouncing between several portals. Choose the region, province, municipality, sheet, and parcel; each step filters the next one and moves the map to the right place.

That is five understandable choices to reach one exact record among millions, and a rare case of software removing work instead of creating more of it.

### Example 4: small update

#### Italiano

Ora si può entrare nell'app con un link ricevuto via email, senza scegliere un'altra password da dimenticare: un click e si entra, mentre chi preferisce la password può continuare a usarla. La mail per ora è piuttosto spartana; prima sistemiamo l'accesso, poi le mettiamo una giacca decente.

#### English

You can now sign in through a link sent by email, without creating another password to forget. It takes one click, while password login is still available for anyone who prefers it. The email is fairly plain for now, but the door works; we can worry about the paint next.

## Failure modes

Do not:

- reuse the same opening or joke in every post;
- turn ordinary bug fixes into heroic launches;
- paste Italian idioms into the English version;
- insert facts from these examples into an unrelated product;
- fabricate a benchmark because numbers make the style look credible;
- add a wall of hashtags, checkmark bullets, or engagement questions;
- isolate every sentence in its own paragraph or use short fragments as the default cadence;
- end every post with a polished aphorism, symmetrical contrast, or mandatory punchline;
- confuse informality with carelessness;
- imitate surface quirks so aggressively that the update becomes parody.
