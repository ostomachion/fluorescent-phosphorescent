# JSON files are run through jsonproc, which is a tool that converts JSON data to an output file
# based on an Inja template. https://github.com/pantor/inja

AUTO_GEN_TARGETS += $(DATA_SRC_SUBDIR)/region_map/region_map_entries.h
$(DATA_SRC_SUBDIR)/region_map/region_map_entries.h: $(DATA_SRC_SUBDIR)/region_map/region_map_sections.json $(DATA_SRC_SUBDIR)/region_map/region_map_sections.json.txt
	$(JSONPROC) $^ $@

$(C_BUILDDIR)/region_map.o: c_dep += $(DATA_SRC_SUBDIR)/region_map/region_map_entries.h

AUTO_GEN_TARGETS += include/constants/region_map_sections.h
include/constants/region_map_sections.h: $(DATA_SRC_SUBDIR)/region_map/region_map_sections.json $(DATA_SRC_SUBDIR)/region_map/region_map_sections.constants.json.txt
	$(JSONPROC) $^ $@

AUTO_GEN_TARGETS += $(DATA_SRC_SUBDIR)/heal_locations.h
$(DATA_SRC_SUBDIR)/heal_locations.h: $(DATA_SRC_SUBDIR)/heal_locations.json $(DATA_SRC_SUBDIR)/heal_locations.json.txt
	$(JSONPROC) $^ $@

$(C_BUILDDIR)/heal_location.o: c_dep += $(DATA_SRC_SUBDIR)/heal_locations.h

AUTO_GEN_TARGETS += include/constants/heal_locations.h
include/constants/heal_locations.h: $(DATA_SRC_SUBDIR)/heal_locations.json $(DATA_SRC_SUBDIR)/heal_locations.constants.json.txt
	$(JSONPROC) $^ $@

# Species info generation from JSON (using grouping wrapper for preprocessor optimization)
SPECIES_TEMPLATE := $(DATA_SRC_SUBDIR)/pokemon/species_info/families.json.txt
JSONPROC_GROUPING := python3 tools/jsonproc_with_grouping.py

# Gen 1-9 families
AUTO_GEN_TARGETS += $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_1_families.h
$(DATA_SRC_SUBDIR)/pokemon/species_info/gen_1_families.h: $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_1_families.json $(SPECIES_TEMPLATE)
	$(JSONPROC_GROUPING) $< $(SPECIES_TEMPLATE) $@

AUTO_GEN_TARGETS += $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_2_families.h
$(DATA_SRC_SUBDIR)/pokemon/species_info/gen_2_families.h: $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_2_families.json $(SPECIES_TEMPLATE)
	$(JSONPROC_GROUPING) $< $(SPECIES_TEMPLATE) $@

AUTO_GEN_TARGETS += $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_3_families.h
$(DATA_SRC_SUBDIR)/pokemon/species_info/gen_3_families.h: $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_3_families.json $(SPECIES_TEMPLATE)
	$(JSONPROC_GROUPING) $< $(SPECIES_TEMPLATE) $@

AUTO_GEN_TARGETS += $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_4_families.h
$(DATA_SRC_SUBDIR)/pokemon/species_info/gen_4_families.h: $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_4_families.json $(SPECIES_TEMPLATE)
	$(JSONPROC_GROUPING) $< $(SPECIES_TEMPLATE) $@

AUTO_GEN_TARGETS += $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_5_families.h
$(DATA_SRC_SUBDIR)/pokemon/species_info/gen_5_families.h: $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_5_families.json $(SPECIES_TEMPLATE)
	$(JSONPROC_GROUPING) $< $(SPECIES_TEMPLATE) $@

AUTO_GEN_TARGETS += $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_6_families.h
$(DATA_SRC_SUBDIR)/pokemon/species_info/gen_6_families.h: $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_6_families.json $(SPECIES_TEMPLATE)
	$(JSONPROC_GROUPING) $< $(SPECIES_TEMPLATE) $@

AUTO_GEN_TARGETS += $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_7_families.h
$(DATA_SRC_SUBDIR)/pokemon/species_info/gen_7_families.h: $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_7_families.json $(SPECIES_TEMPLATE)
	$(JSONPROC_GROUPING) $< $(SPECIES_TEMPLATE) $@

AUTO_GEN_TARGETS += $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_8_families.h
$(DATA_SRC_SUBDIR)/pokemon/species_info/gen_8_families.h: $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_8_families.json $(SPECIES_TEMPLATE)
	$(JSONPROC_GROUPING) $< $(SPECIES_TEMPLATE) $@

AUTO_GEN_TARGETS += $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_9_families.h
$(DATA_SRC_SUBDIR)/pokemon/species_info/gen_9_families.h: $(DATA_SRC_SUBDIR)/pokemon/species_info/gen_9_families.json $(SPECIES_TEMPLATE)
	$(JSONPROC_GROUPING) $< $(SPECIES_TEMPLATE) $@

# Test families (separate template)
AUTO_GEN_TARGETS += $(DATA_SRC_SUBDIR)/pokemon/species_info/test_families.h
$(DATA_SRC_SUBDIR)/pokemon/species_info/test_families.h: $(DATA_SRC_SUBDIR)/pokemon/test_families.json $(DATA_SRC_SUBDIR)/pokemon/test_families.json.txt
	$(JSONPROC) $^ $@
