"""R30 NEXT SOURCE cycle only: physical Caviar 2x8 versus Soho Ivory 2x10 niche risk models.
No critic packets, owner selection, replacement champion, PO, or new wet-wall permission.
"""
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
import csv
R=Path(__file__).resolve().parents[1]
O=R/'research/products'
out=O/'R30_PH4_TX4_24_NICHE_2X8_VS_2X10_WET_AND_TRIM_FORMAT_SCENARIOS.csv'
assert not out.exists()
d=lambda x: Decimal(str(x))
n=lambda x: str(d(x).quantize(d('.0001'),rounding=ROUND_HALF_UP))
materials=[
 ('Clara Tierra Madre Caviar','2x8',d('8'),d('13'),'INDIVIDUAL_CAVIAR_WET_NICHE_NOT_LISTED_SYSTEM_INSTALLATION_PDF_ALONE_NOT_CLEARANCE'),
 ('ELM Soho Ivory','2x10',d('10'),d('9.5'),'INDIVIDUAL_SOHO_IVORY_WET_WALL_LISTED_BUT_ORDERABLE_SKU_LOT_NOT_VERIFIED')
]
rooms=[('PH-BATH4',d('111'),'CONFIRMED_WALKIN_BRIZO_BNX_4IN_SQUARE_POINT_FOURPLANE_PAN_SEPARATE'),
 ('TX-BATH4',d('93'),'CONFIRMED_DURAVIT_TUB_HANSGROHE_MATTE_WHITE_NO_PAN')]
rows=[]
for room,height,fixture in rooms:
 for name,fmt,mod,thick,permission in materials:
  for width in (12,16,24):
   for joint in (d('.125'),d('.1875')):
    wall=d('30.48');h=d(12);depth=d(4)
    back=d(width)*h/d(144)
    sides=2*h*depth/d(144);twoends=2*d(width)*depth/d(144)
    pier=(wall-d(width)-2*joint)/2
    viable=[(count,(d(width)-count*mod-(count+1)*joint)/2) for count in range(6)]
    viable=[(a,b) for a,b in viable if 0<b<=mod]
    selected=max(viable,key=lambda a:a[0]) if viable else (0,d('0'))
    rows.append(dict(room=room,original_owner_program_and_selected_fixture=fixture,original_niche_material='Clara Tierra Madre Caviar 2x8 13mm unverified individual wet NICHE',
      hypothetical_maker_material_AND_NO_OWNER_SELECTION=name,nominal_tile_size=fmt,nominal_manufacturer_body_thickness_mm=n(thick),
      maker_specific_wet_NICHE_evidence=permission,current_factory_orderable_SKU_caliber_lot='',actual_wall_wet_listing_elsewhere='ORIGINAL_PH4_RIBBED_UNLISTED' if room=='PH-BATH4' else 'TX4_FLAT_CHARCOAL_WET_LISTING_REVALIDATE',
      W3_prior_width_in_NOT_VERIFIED=n(wall),W3_prior_tiled_height_in_NOT_VERIFIED=n(height),
      hypothetical_niche_opening_width_in=str(width),hypothetical_niche_opening_height_in='12',hypothetical_reveal_depth_in='4',
      hypothetical_grout_joint_in=n(joint),hypothetical_nominal_full_horizontal_tile_count=selected[0],
      hypothetical_balanced_horizontal_tile_end_each_in=n(selected[1]),hypothetical_W3_side_pier_after_joint_each_in=n(pier),
      W3_side_pier_under_three_in='TRUE' if pier<3 else 'FALSE',
      one_displaced_FIELD_wet_WALL_aperture_SF=n(back),one_niche_BACK_SF=n(back),two_SIDE_returns_SF=n(sides),
      TOP_plus_SILL_SF=n(twoends),nominal_niche_tile_NET_without_waste_SF=n(back+sides+twoends),
      indicative_nominal_thickness_difference_if_Soho_vs_Caviar_mm='3.5',actual_finished_tile_mortar_substrate_edge_elevation_delta_mm='',
      actual_niche_location_count_and_finish_verified='FALSE',current_case_SKU_stock_price_installed_bid='',
      manufacturer_approved_combined_waterproof_membrane_shop='FALSE',owner_wet_wall_and_niche_selected='FALSE',
      architect_1529_shop_signed='FALSE',tile_installer_1to1_cut_and_trim_test='FALSE',supplier_lot_release='FALSE',GC_release='FALSE',purchase_authorized='FALSE'))
assert len(rows)==24
with out.open('w',encoding='utf-8',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
print('PASS R30 next substantive 24 Caviar vs Soho maker wet/format/return/pier/plane-detail source study, no release')
