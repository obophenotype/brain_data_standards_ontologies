# set your working directory
studydir <- paste0("Desktop/Reference genomes/Reference gene files/")

# import gtf
Human_gene <- rtracklayer::import('Desktop/Reference genomes/Reference gene files/human_genes.gtf')
Human_gene_df=as.data.frame(Human_gene)

marmoset_gene <- rtracklayer::import('Desktop/Reference genomes/Reference gene files/marmoset_genes.gtf')
marmoset_gene_df=as.data.frame(marmoset_gene)

# write tsv
write.table(Human_gene_df, file='Desktop/Reference genomes/Reference gene files/human_genes.tsv', col.names = NA, sep="\t")
write.table(marmoset_gene_df, file='Desktop/Reference genomes/Reference gene files/marmoset_genes.tsv', col.names = NA, sep="\t")

#simplify tables
simple_human <- Human_gene_df[ -c(1:5,8:9,11,13,16,19:22) ]
simple_marmoset <- marmoset_gene_df[ -c(1:5,7:9,12:19) ]
simple_marmoset <- simple_marmoset[!duplicated(simple_marmoset[,3]), ]

# write simple tsv                      
write.table(simple_human, file='Desktop/Reference genomes/Reference gene files/simple_human.tsv', col.names = NA, sep="\t")
write.table(simple_marmoset, file='Desktop/Reference genomes/Reference gene files/simple_marmoset.tsv', col.names = NA, sep="\t")
