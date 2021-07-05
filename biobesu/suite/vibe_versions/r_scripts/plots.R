########
# Name:
# plots.R
#
# Description:
# Generates plots for this biobesu benchmark suite.
#
# Important:
# When adjusting the benchmark versions, be sure to add/remove `make_option` in `options`
# and adjust the items in `benchmarkedVersions` (both can be found in the Config section).
# 
# When running through RStudio:
# Be sure to add the input files to this directory or change the default paths.
#
# When running through the command line (Rscript):
# `cd` to the directory containing this script and add the input files to this directory
# or give all paths as arguments.
########

##################
### Config     ###
##################

# Input arguments.
# Change the arguments here if adding/remove benchmarks from the plots!
library(optparse)
options = list(
  make_option(c("-b", "--benchmark"), help="path to benchmark .tsv file", default="./benchmark_data.tsv"),
  make_option(c("--lirical"), help="path to VIBE lirical .tsv file", default="./vibe_lirical.tsv"),
  make_option(c("--v2.0"), help="path to VIBE v2.0 .tsv file", default="./vibe_2.0.tsv"),
  make_option(c("--v5.0"), help="path to VIBE v5.0 .tsv file", default="./vibe_5.0.3.tsv"),
  make_option(c("-o", "--output"), help="directory to write plots to", default="./")
);

# Names of the different benchmarks as retrieved from digested command line.
# Change the arguments here if adding/remove benchmarks from the plots!
benchmarkedVersions <- c("lirical", "v2.0", "v5.0")

# Configuration based on whether run through RStudio or through command line Rscript.
if(interactive()) {
  # Sets working directory to script dir.
  setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
} else {
  # Disables writing Rplots.pdf file when script is done.
  pdf(NULL)
}

##################
### Libraries  ###
##################

library(rcartocolor)
library(plyr)
library(dplyr)
library(reshape2)
library(ggplot2)

##################
### Functions  ###
##################

########
# Name:
# ggSaveCustom
#
# Description:
# A simple wrapper for writing a file using ggsave that prepends the directory
# and appends the file extension.
#
# Input:
# fileName - Filename (excluding file extension) to be used for storage.
# width	- The width of the device in inches. -> see ?ggsave()
# height - The height of the device in inches. -> see ?ggsave()
#
# Output:
#
########
ggSaveCustom <- function(fileName, width, height) {
  ggsave(paste0(params$output, fileName, ".pdf"), width=width, height=height)
}

########
# Name:
# readResultFile
#
# Description:
# Reads in a single file containing benchmarking results.
#
# Input:
# filePath -  The path to the file to be loaded.
#
# Output:
# A table from the result data. Though as the input is expected to only contain
# 2 columns and one of these is used as row names, type becomes a list.
########
readResultFile <- function(filePath) {
  read.table(filePath, header=T, sep="\t", colClasses=c("character"), row.names=1)
}

########
# Name:
# sortRows
#
# Description:
# Orders the rows based on their row name.
#
# Input:
# benchmarkResults - All the output from a benchmark. Each row contains the LOVD
#                    as row name and the ordered genes as a column named "genes"
#                    (these genes are comma-separated within this single field).
#
# Output:
# benchmarkResults with the rows ordered on their name.
########
sortRows <- function(benchmarkResults) {
  benchmarkResults[order(as.numeric(rownames(benchmarkResults))), , drop=FALSE]
}

########
# Name:
# resultsPositionCalculator
#
# Description:
# For each row in benchmarkData (containing an ID and a gene), looks at the
# benchmarkResults to determine the gene positions.
#
# Input:
# benchmarkData - The data on which the benchmark is based upon. Should at least
#                 contain a column "gene" containing the gene to be found
#                 (determening the gene position) and "lovd" to determine the ID
#                 of which phenotype-set was used.
# benchmarkResults - All the output from a benchmark. Each row contains the LOVD
#                    as row name and the ordered genes as a column named "genes"
#                    (these genes are comma-separated within this single field).
#
# Output:
# 
########
resultsPositionCalculator <- function(benchmarkData, benchmarkResults) {
  apply(benchmarkData, 1, singleResultPositionCalculator,
        benchmarkResults=benchmarkResults)
}

########
# Name:
# singleResultPositionCalculator
#
# Description:
# Processes a single row of the benchmarkData as defined in the function
# resultsPositionCalculator. For this single benchmark slice, it looks up the
# corresponding ID in benchmarkResults and then defines the gene position.
#
# Input:
# benchmarkDataRow - A list (row from benchmarkData given by
#                    resultsPositionCalculator) containing an ID and a gene.
# benchmarkResults - All the output from a benchmark. Each row contains the ID
#                    as row name and the ordered genes as a column named "genes"
#                    (these genes are comma-separated within this single field).
#
# Output:
# 
########
singleResultPositionCalculator <- function(benchmarkDataRow, benchmarkResults) {
  match(benchmarkDataRow["gene_id"],
        strsplit(benchmarkResults[benchmarkDataRow["id"],"suggested_genes"], ",")[[1]])
}

########
# Name:
# calculateTotalGenesFound
#
# Description:
# Calculates the total number of genes per item for the input list benchmarkResults.
#
# Input:
# benchmarkResults - All the output from a benchmark. Each row contains the LOVD
#                    as row name and the ordered genes as a column named "genes"
#                    (these genes are comma-separated within this single field).
#
# Output:
# An integer vector containing the total number of genes for each (named) item
# (in the row order of benchmarkResults).
########
calculateTotalGenesFound <- function(benchmarkResults) {
  unlist(lapply(sapply(benchmarkResults[,"suggested_genes"], strsplit, split=","), length), use.names=FALSE)
}

##################
###    Code    ###
##################

###
### Digest command line
###
params = parse_args(OptionParser(option_list=options));


# Load benchmark input data (with ncbi gene id's).
benchmarkData <- read.table(params$benchmark, header=T, sep="\t", colClasses=c("character"))

# Generates variables to store data in.
resultData <- list()
positionResults <- data.frame(matrix(nrow=nrow(benchmarkData)), row.names=benchmarkData$id)
totalResults <- data.frame(matrix(nrow=nrow(benchmarkData)), row.names=benchmarkData$id)

# Digests all results.
for(version in benchmarkedVersions) {
  resultData[[version]] <- sortRows(readResultFile(params[[version]]))
  positionResults[[version]] <- resultsPositionCalculator(benchmarkData, resultData[[version]])
  totalResults[[version]] <- calculateTotalGenesFound(resultData[[version]])
}
rm(version)

# Removes initial empty matrix.
positionResults <- positionResults[,-1]
totalResults <- totalResults[,-1]

# Generate splitted genes for all tools: [[version]][[id]]@genes[[1]]
setClass("suggestedGenes", representation(genes="vector"))
toolOutputSplitted <- sapply(resultData, function(versionData) {
  sapply(rownames(versionData), function(id, versionData) {
    new("suggestedGenes", genes=strsplit(versionData[id,"suggested_genes"], ","))
  }, versionData=versionData)
}, simplify=FALSE)
names(toolOutputSplitted) <- names(resultData)

# Tool colors
toolColors <- carto_pal(length(resultData), "Safe")
names(toolColors) <- names(resultData)

##############################
########## FIGURE 1 ##########
##############################
### Scatterplot with means and missing

# Preperations.
posRelM <- melt(positionResults, id.vars = 0)
totResM <- melt(totalResults, id.vars = 0)
posRelM$total <- totResM$value
colnames(posRelM) <- c("tool", "rank", "total")
posRelM$relative <- posRelM$rank / posRelM$total

gd <- posRelM %>% 
  group_by(tool) %>% 
  summarise(total = mean(total, na.rm=T),
            rank  = mean(rank, na.rm=T))
toolNaRanks <- aggregate(rank ~ tool, data=posRelM, function(x) {sum(is.na(x))}, na.action = NULL)
gd$NAs <- paste(toolNaRanks$tool, " (", toolNaRanks$rank, " missed)", sep="")

gd$labX <- c(10, 130, 1200)
gd$labY <- c(30000, 30000, 30000)

# Plotting figure.
ggplot() +
  geom_point(data = posRelM, aes(x=total, y=rank, color=tool), size = 0.3) +
  geom_point(data = gd, aes(x=total, y=rank, fill=tool), shape = 21, color = "black", stroke = 1, size = 2) +
  # legend stuff
  geom_point(aes(x=11, y=150), color = "black", size=0.3) +
  geom_text(aes(x=11, y=150, label = "= one causal gene"), color = "black", size = 2, hjust = 0, nudge_x = 0.1) +
  geom_point(aes(x=11, y=300), shape = 1, color = "black", stroke = 1, size = 2) +
  geom_text(aes(x=11, y=300, label="= tool X and Y means"), color="black", hjust = 0, size = 2, nudge_x = 0.1) +
  geom_text(aes(x=8.5, y=30, label="Total: 308\ncausal genes"), color="black", hjust = 0, size = 2, nudge_x = 0.1) +
  geom_label(data = gd, aes(x = labX, y = labY, label = NAs, fill = tool), color="white", hjust = 0, size = 2, fontface = "bold") +
  scale_y_log10(breaks = c(1, 10, 100, 1000, 10000)) + scale_x_log10(breaks = c(1, 10, 100, 1000, 10000, 40000)) +
  theme_bw() +
  theme(panel.grid = element_blank(), panel.border = element_rect(colour = "black"), axis.ticks = element_line(colour = "black"), legend.position = "none", axis.text = element_text(color = "black")) +
  scale_color_manual(values = toolColors) +
  scale_fill_manual(values = toolColors) +
  labs(x = "Total number of candidate genes returned", y = "Rank of the causal gene")

ggSaveCustom("fig1", width=4, height=2.5)

# Removes variables specific to this section.
rm(posRelM,totResM,gd,toolNaRanks)
