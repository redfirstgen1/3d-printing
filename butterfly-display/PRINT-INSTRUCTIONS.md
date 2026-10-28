# Butterfly and roses — Snapmaker U1

This is a procedural interpretation of the supplied concept image, not an exact reconstruction. It uses rounded floral petals and structural wing ribs. The generated preview shows the actual model. Dimensions and mesh checks are recorded in validation.json.

## Open in Snapmaker Orca

1. Select your installed Snapmaker U1 profile with 0.4 mm nozzles. Use the printer manufacturer's current profile; this package does not contain a machine profile or G-code.
2. Import butterfly-display.3mf as geometry. Keep Black and White together as parts of one object, preserving their alignment. Assign Black to black PLA and White to white/ivory PLA. If the importer flattens the model, import black.stl and white.stl together and answer Yes when asked to load them as one object with multiple parts. Do not auto-arrange the two colors separately.
3. Keep the circular base flat on the build plate. Check the overall dimensions against validation.json. STL units are millimeters.
4. Start with 0.16 mm layers, 3 walls, 15% gyroid infill, 4 top/bottom layers, and the PLA temperature/cooling settings supplied by your filament profile. Use a 5 mm brim if adhesion needs help.
5. Enable organic/tree supports and inspect their placement around the wings, scrolls, rose petals, and antennae. Start with supports everywhere: build-plate-only supports may miss surfaces hidden behind the base or lower wings. Avoid support contacts on thin antennae where practical. A support interface with roughly 0.2 mm top Z distance is a starting point for same-material PLA, not a verified setting.
6. Slice and inspect every layer, especially the first layer of each white bead, the wing cells, and antenna tips. Check that both filaments have extrusion paths, color changes use the intended tools, and supports reach all floating starts. Use Orca's overhang and toolpath preview; resolve any warnings before printing.
7. Estimate time and filament in Orca after slicing. The reference image's 3–4 hour / 35–45 g figures are unverified and are not estimates for this model.

## Validation and limitations

The build script checks mesh manifold edges and calculates volumes. Those checks do not establish physical print success. This model has not been sliced in Snapmaker Orca or physically test printed. Decorative antennae and wing edges remain fragile; remove supports carefully. The two colors share a material boundary, so keep both parts at their original coordinates. At this small scale, fine roses are stylized; enlargement improves detail but also increases support use.

Files: multipart 3MF, separate color STL files, editable Blender scene, procedural Blender Python source, geometry preview, and validation report. The 3MF is a geometry package, not a saved Snapmaker Orca project with verified printer settings.

To regenerate with Blender 4.3: `blender -b -t 4 --python create_model.py` from this folder. This overwrites generated outputs.
