# Fixture catalog

| Fixture | Selected configuration | Nominal dimensions / installation | Final RFA |
|---|---|---|---|
| Maverick II LED fan | Matte black | 52 in sweep; 13.8 in manufacturer overall height | `Visual_Comfort_Maverick_II_3MAVR52BKBKD_R2025.rfa` |
| FLOS IC C/W1 | Brass / opal | 7.9 W x 8.5 H x 11 D in | `FLOS_IC_CW1_FU317859_Brass_Opal_R2025.rfa` |
| AERIN Brenta | Bronze / white and clear glass | 3.5 W x 18.5 H x 3.75 D in | `AERIN_Brenta_ARN2473BZ-CG_Bronze_R2025.rfa` |
| Forked Shade pendant | Brass; medium 9.8 in selection | 9.84 dia; 18.8 body height; 37.82 installed drop in | `BusterPunch_Forked_Shade_Brass_9_84_R2025.rfa` |
| RBW Dimple | Black anodized / amber / 3000 K | 5 dia x 3.3 projection in; 3000 K | `RBW_Dimple_Black_Anodized_Amber_3000K_R2025.rfa` |
| RBW Dimple | Black anodized / white interior / 3000 K | 5 dia x 3.3 projection in; 3000 K | `RBW_Dimple_Black_Anodized_White_Interior_3000K_R2025.rfa` |
| Minka Vantage | Coal; 11 in | 11 dia x 1.5 H in; 3000 K | `Minka_Vantage_759-2-66A-L_Coal_11_R2025.rfa` |
| Nodes Angled sconce | Burnished brass / milk glass | 8 W x 7.63 H x 5.5 D in | `Visual_Comfort_Nodes_KW1041BBS_Burnished_Brass_R2025.rfa` |
| Nodes Angled sconce | Midnight black / milk glass | 8 W x 7.63 H x 5.5 D in | `Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa` |
| Alora Cassia linear pendant | Aged gold / opal matte | 48 W x 13.375 D x 6 body H in; 15.875 installed drop | `Alora_Cassia_LP549448AGOP_R2025.rfa` |
| Il Fanale Madame | Brass | 16.33 H x 14.17 D in; 2.36 in shade diameter | `IlFanale_Madame_28810ON_Brass_R2025.rfa` |
| Kelly Wearstler Covet | Antique-burnished brass / alabaster | 18.25 square x 2.75 H in; 2700 K | `VisualComfort_Covet_KW4115AB-ALB_AntiqueBurnishedBrass_Alabaster_R2025.rfa` |
| Terzani Mizu three-light pendant | Gold crystal; 8.7 in selection | 8.66 W; 8.3 canopy dia; 19.7 installed drop in; 3000 K | `Terzani_Mizu_0R03SE8A4ATE_Gold_8_66_3000K_R2025.rfa` |
| Visual Comfort Orbel | Natural brass / white glass | 5 W x 12.9 H x 6.7 D in | `Visual_Comfort_Orbel_700WSOBLNB_Natural_Brass_R2025.rfa` |

## F01 - Maverick II LED fan

The exact manufacturer specification overrides the retailer 19.8 in height. Supplied 6 in downrod, 6 in canopy, 6.8 in housing and 6.88 x 1.62 in glass informed the model. Blade camber, sweep, thickness, edge shape and recessed trim details are inferred from photographs. Rotor geometry is fixed; materials are editable.

Source: https://www.lightology.com/index.php?module=prod_detail&prod_id=816712&option_id=816709

Builder: `f01_816712/build_f01_816712.py`

## F02 - FLOS IC C/W1

Printed overall dimensions govern. The opal sphere, narrow supporting arm and circular brass mount were compared with the product photograph and dimension drawing. Undimensioned arm, collar and glass wall details are reconstructed.

Source: https://www.lightology.com/index.php?module=prod_detail&prod_id=231180

Builder: `f02_231180/build_ic_cw1.py`

## F03 - AERIN Brenta

Bronze option resolves the finish override in the request. Slightly flared hollow glass shells and inner diffusers follow the official photograph and source-RFA dimensions. Printed nominal envelope overrides slight reference-model differences. The backplate depth and small radii remain inferred.

Source: https://www.lightology.com/index.php?module=prod_detail&prod_id=1241670&option_id=1241668

Builder: `f03_1241670/build_brenta.py`

## F04 - Forked Shade pendant

Manufacturer medium drawing gives 9.84 in shade diameter, 5.9 in shade height and 12.9 in upper assembly. The default 18 in visible cord is a chosen installation, giving 37.82 in total drop including canopy. The shade is open and hollow; fork, machined flutes and shoulder contours are photo-derived. Current retailer and legacy drawing SKUs differ; the medium size is consistent.

Source: https://www.lightology.com/index.php?module=prod_detail&prod_id=1149899

Builder: `f04_1149899/build_forked.py`

## F05 - RBW Dimple

Two RFAs cover S1 white interior and S3 amber cast glass, both black anodized, IP65 configuration and 3000 K. Concave face, rolled edge, cast-glass wall thickness and internal optics are reconstructed from the product photographs. The source color choices are retained separately.

Source: https://www.lightology.com/index.php?module=prod_detail&prod_id=1441643&option_id=1441619

Builder: `f05_1441643/build_dimple.py`

## F06 - Minka Vantage

The 11 in Coal option 759-2-66A-L replaces the generic linked smaller option. The model retains the shallow coal canopy, clear acrylic rim and luminous white diffuser. Unspecified edge rounds and internal diffuser depth are inferred.

Source: https://www.lightology.com/index.php?module=prod_detail&prod_id=1418164&option_id=1418168

Builder: `f06_1418164/build_vantage.py`

## F07 - Nodes Angled sconce

Two RFAs cover KW1041BBS and KW1041MBK. Published backplate is 5.25 dia x .125 in; milk shade is 3.5 dia x 3.25 H in. Reflector tilt/thickness, body profile and socket details are photo/drawing-derived. Readable expanded source is authoritative; older encoded launch files are historical.

Source: https://www.lightology.com/index.php?module=prod_detail&prod_id=833919&option_id=833918

Builder: `f07_833919/build_nodes_payload_expanded.py`

## F08 - Alora Cassia linear pendant

Four 6 in opal globes and 11.125 x 4.375 x .875 in canopy follow the manufacturer drawing. The installed default uses one included 12 in rod per support; support spacing, bar diameters and socket collars are inferred. The 46 in maximum suspension is not the default modeled installation.

Source: https://www.lightology.com/index.php?module=prod_detail&prod_id=1104949

Builder: `f08_1104949/build_cassia.py`

## F09 - Il Fanale Madame

The dimension graphic identifies 2.36 in as the cylindrical shade diameter. Its hemispherical wall cover is larger: modeled at 4 in diameter by drawing/photo proportion, so actual overall model width is 4 in. This is disclosed inference, not a manufacturer canopy dimension. Arch, joints, bell shoulder and hollow shade follow the reference.

Source: https://www.lightology.com/index.php?module=prod_detail&prod_id=1254269&option_id=1254270

Builder: `f09_1254269/build_madame.py`

## F10 - Kelly Wearstler Covet

The exact linked option governs. Stone is widest at its ceiling edge and tapers inward toward the exposed underside. Two opposite-side brass retainers follow the photograph and reference solids. The companion alabaster image is cropped from the exact product image and bound to diffuse and luminous color. Natural-stone variation and material luminance are visual approximations.

Source: https://www.lightology.com/index.php?module=prod_detail&prod_id=1242580&option_id=1242586

Builder: `f10_1242580/build_covet.py`

## F11 - Terzani Mizu three-light pendant

The LED 3000 K option 0R03SE8A4ATE replaces the linked Xenon option. Three independently varied cast-crystal profiles and etched inner cores follow the gold reference images. Crystal contours, 3.6 in modeled width, cable locations and stagger are inferred. The fixed default uses the documented 19.7 in minimum overall installation.

Source: https://www.lightology.com/index.php?module=prod_detail&prod_id=1476233&option_id=1476232

Builder: `f11_1476233/build_mizu.py`

## F12 - Visual Comfort Orbel

Natural-brass 700WSOBLNB resolves the requested finish rather than the original aged-brass default. The rectangular backplate, perpendicular fin and opal globe match the source silhouette. Plate .7 in depth is published; remaining small transition and globe details are inferred.

Source: https://www.lightology.com/index.php?module=prod_detail&prod_id=813073&option_id=1279684

Builder: `f12_813073/build_f12_orbel.py`
