# Adella Viso White — high-resolution photo review

Revit 2025 ADSKLIB, V-Ray VRMAT/VRSCENE, and required textures.

Extract all files to a permanent folder. In Revit, open the library in Manage > Materials and add the material to the project. Repath BOTH Appearance color and bump images to this package's textures folder. The library's existing absolute paths also resolve to refreshed maps in output/adella/textures on this computer. Revit may cache images: reload/repath textures and restart the render before comparing. Do not use the older nested extracted package.

V-Ray: import the VRMAT, repath its three bitmap files to this textures folder, and use mapping channel 1 at 24.0625 x 12.0625 inches per repeat. The purple RGB16 image is a tangent-space OpenGL NORMAL map (linear/raw), not grayscale height. Adella_Bump.png and Adella_Height16.png are 16-bit grayscale height, also linear/raw. Displacement is not enabled. Avoid applying both the Revit bump and an additional V-Ray bump to the same surface.

Source: StoneLocator's single-tile photograph, 2560 x 1269 pixels. Output maps are resampled to 4096 x 2048; this does not create native 4K detail. Relief is inferred from a lit photograph, not measured height. Color shading is attenuated, not scientifically calibrated. Relief full-range scaling is an estimated 0.6 mm, with shallower photographed facet variation.

This revision fixes intermediate 8-bit quantization by retaining floating-point values through smoothing, resizing and gradient calculation. Both height and normal textures are exported at 16 bits. Preview is an illustrative shaded map, not a native Revit/V-Ray render. Native appearance remains subject to your review; prior claims that all rendering artifacts were eliminated were unsupported.
