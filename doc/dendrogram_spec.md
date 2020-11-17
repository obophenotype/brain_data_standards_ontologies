### Taxonomy variables  

`taxonomy_id` is the name of the taxonomy in the format: <CCN><YYYYMMDD><T>, where:  

* CCN stands for "Common Cell type Nomenclature"
* YYYYMMDD represents an 8 digit date format (Y=year, M=month, D=day)
* T is a 1-digit taxonomy counter, which allows up to 10 taxonomies on the same date  
  
If more than 10 taxonomies are being generated on a single date, it is reasonable to increment or decrement the data by a day to ensure uniqueness of taxonomies.  More generally, to keep taxonomy IDs unique, **please select a taxonomy_id [NOT IN THIS TABLE](https://docs.google.com/spreadsheets/d/10gYNyOhc0YHOYKjgsvLfumf65CqLeiVDCE3Wrxz4Txo/edit?usp=sharing), and add your taxonomy_ID to the table as needed.**  Strategies for better tracking of taxonomy IDs are currently under consideration , including a Cell Type Taxonomony Service currently in development for Allen Institute taxonomies, additional databasing options for the [Brain Initiative - Cell Census Network (BICCN)](https://biccn.org/), a [Cell Annotation Platform (CAP)](https://github.com/kharchenkolab/cap-example/) under development as part of the [Human Cell Atlas](https://www.humancellatlas.org/), and likely other options.  One future goal will be to centralize these tracking services and replace the above table.  
	
`taxonomy_author` is the name of a point person for this taxonomy (e.g., someone who is responsible for it's content).  This could either be the person who built the taxonomy, the person who uploaded the data, or the first or corresponding author on a relevant manuscript.  By default this person is the same for all cell_sets; however, there is opportunity to manually add additional aliases (and associated assignees and citations that may be different from the taxonomy_author) below.  
  
`taxonomy_citation` is a the citation or permanent data identifier corresponding to the taxonomy (or "" if there is no associated citation).  Ideally the DOI for the publication will be used, or alternatively some other permanent link.  
	
`anatomic `structure`.  This represents the location in the brain (or body) from where the data in the taxonomy was collected.  Ideally this will be linked to a standard ontology via the `ontology_tag`.  In this case, we choose "middle temporal gyrus" from ["UBERON"](http://uberon.github.io/) since UBERON is specifically designed to be a species-agnostic ontology and we are interested in building cross-species brain references.  It is worth noting that these structures can be defined separately for each cell set at a later step, but in the initial set-up only a single structure can be input for the entire taxonomy.  


### Cell set variables

* `cell_set_accession`^: The unique identifier (cell set accession id) assigned for each cell set of the format <CS><YYYYMMDDT>_<#>, where CS stands for cell set, <YYYYMMDDT> matches the taxonomy_id (see above), and the # is a unique number starting from 1 for each cell set.  
* `original_label`: The original cell type label in the dendrogram.  This is used for QC only but is not part of the CCN.  
* `cell_set_label`: A label of the format <first_label> <#>.  If only a single first_label was input above, these numbers will match the <#> from cell_set_accession.  This used to be part of the CCN and is now deprecated, but critical but useful for coding purposes.  
* `cell_set_preferred_alias`^: This is the label that will be shown in the dendrogram and should represent what you would want the cell set to be called in a manuscript or product.  If the CCN is applied to a published work, this tag would precisely match what is included in the paper.  
* `cell_set_aligned_alias`^: This is a special tag designed to match cell types across different taxonomies.  We discuss this tag in great detail in our manuscript, and will be discussed briefly below.  As output from `build_nomenclature_table`, this will be blank for all cell sets.  
* `cell_set_additional_aliases`^: Any additional aliases desired for a given cell set, separated by a "|".  For example, this allows inclusion of multiple historical names.  As output from `build_nomenclature_table`, this will be blank for all cell sets.  
* `cell_set_structure`^: The structure, as described above.  Can be modified for specific cell sets below.  Multiple cell_set_structures can be given separated by a "|".  
* `cell_set_ontology_tag`^: The ontology_tag, as described above.  Can be modified for specific cell sets below.  Multiple cell_set_ontology_tags can be given separated by a "|", and must match cell_set_structure above.
* `cell_set_alias_assignee`: By default the taxonomy_author, as described above. In this case, if aliases are assigned by different people, additional assignees can be added by separating using a "|".  The format is [preferred_alias_assignee]|[aligned_alias_assignee]|[additional_alias_assignee(s)].  If aliases are added without adding additional assignees it is assumed that the assignee is the same for all aliases.  
* `cell_set_alias_citation`: By default the taxonomy_citation, as described above (or can be left blank). In this case, if preferred (or other) aliases are assigned based on a different citation, additional citations can be added by separating using a "|", with the same rules as described by cell_set_alias_assignee.  Ideally the DOI for the publication will be used (or another permanent link).  
* `taxonomy_id`^: The taxonomy_id, as described above.  This should not be changed.  
