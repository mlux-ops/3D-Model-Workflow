# Quorum Veno 858-59 - R02 evidence and restrictions (2026-10-16)

**Status: UNEXECUTED / UNAPPROVED candidate.** The prior R01 family passed
Revit technical geometry and placement QA but its appearance was not approved.
No native execution of R02 is authorized by this review.

## Official sources

- Product: https://quoruminternational.com/products/858-59
- Exact manufacturer PDF: https://images.junipercdn.com/3206/application-assets/juniper-web/product%20cut%20sheets/858-59.pdf
- Legacy product page: https://www.quoruminternational.com/categories/23097/ceiling-mount/products/858-59/veno-1-light-pendant
- Manufacturer successor retailer: https://www.quorumhome.com/products/858-59

The exact manufacturer's 858-59 PDF returned HTTP 200 and Content-Type
application/pdf, 265600 bytes on October 16, 2026. Parsed manufacturer PDF
identifies *Veno 858-59 VENO 1 Light Pendant* and gives:

| Attribute | OEM-supported |
|---|---|
| Fixture | 11.00 in diameter, 19.00 in height |
| Shade | 11.25 in height; exact profile and diameter unlabelled |
| Canopy | 4.75 in diameter x 0.75 in height |
| Metal / glass | Matte Black steel; clear glass |
| Lamp | One medium-base E26 socket, 100W maximum; lamp not included |
| Included stems | Two 8 in, two 12 in, two 16 in |
| Included chain | 1 ft black chain |
| Cord | 10 ft black |
| Rating | Damp-listed |
| Weight | 8 lb |

Manufacturer's product page corroborates the dimensions and suspension list.
The 19 in height is the **fixture body**, not ceiling-to-bottom overall drop.
24 in of stems (two included 12 in sections) is a feasible *selected installation*
but no fixed 24 in minimum or universal hanging configuration is established.

## R01 / R02 correction list

1. **Glass:** R01 made 12 disconnected glass bars 0.21 in square; they do
   not represent an actual clear glass shade. R02 uses one contiguous annular
   glass volume with an open bottom and separately editable glass material.
   The circular section and nominal 0.125 in glass wall are **inferred**,
   not OEM dimensional claims. Manufacturer imagery must establish the exact
   silhouette, whether facets exist, and any flat or tapered surfaces.
2. **Shade height:** R01 has no 11.25 in glass-height parameter and spans
   roughly 16 in using bars. R02 explicitly sets the OEM 11.25 in shade-height
   parameter and locates the shade inside the 19 in body envelope.
3. **Suspension:** R01 calls 24 in rods arbitrary. R02 explains a 24 in
   example as two manufacturer-supplied 12 in sections; also records available
   8 / 12 / 16 in rods and 12 in chain. The chain remains optional/unmodeled.
4. **Metal frame:** R01 11 in upper/lower metal circular rings plus 12 glass
   slivers assert unsupported detailing. R02 removes bottom metal ring and
   leaves only schematic coupler, retainer and socket. Manufacturer describes
   an *angular frame* but exact metal members remain unverified; the R02
   proxy is not a faithful finished appearance.
5. **Photometry:** E26 bulb is selected separately; no OEM product-specific
   IES file or MEP electrical connector was located. Do not assign a made-up
   IES intensity distribution or lumen value.

## CAD, IES and source limitations

Searches of Quorum's official model page and indexed product/download
resources did not establish an exact matching OEM **RFA, DWG, DXF, OBJ, STEP,
or IES** for the 858-59. The PDF is the highest-confidence dimension source.
Product photographs help assess silhouette, but photographs without measured
side views cannot establish accurate section geometry, angular frame spacing
or thickness. Other Veno family SKUs cannot substitute as exact geometry.
An unrelated 678-series installation instruction PDF was found, but it
does not identify 858-59 and is excluded as model evidence.

## Acceptance gate

R02 must be inspected against front/side/oblique manufacturer photographs and
native Revit 2025 save/reopen, face-placement, dimensions, glass material
substitution and warning checks. The existing QA script's 43-inch expected
height applies to the chosen 24-inch stem plus 19-inch body, and does not
validate any OEM minimum or maximum installation drop. Do not mark R02
APPROVED until optical and silhouette review establishes fixture fidelity.
