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
# 1. Copy the `benchmark_data.tsv` to the directory of this script.
# 2. Create a subdirectory called `results`.
# 3. Copy the merged output scripts from the benchmark runs into this directory.
# 4. Run through RStudio.
#
# When running through the command line (Rscript):
# Run it with `RScripts` and provide all paths through the command line arguments OR
# do step 1-3 above, `cd` to the directory of this script and run it through `RScript` without arguments
########



##################
### Libraries  ###
##################

library(optparse)
library(rcartocolor)
library(plyr)
library(dplyr)
library(reshape2)
library(ggplot2)
library(grid)



##################
### Config     ###
##################

# Input arguments.
options = list(
  make_option(c("-b", "--benchmark"), help="path to benchmark .tsv file", default="~/Programming/data/biobesu/benchmark_data/moon.tsv"),
  make_option(c("-r", "--results"), help="directory containing the benchmark result .tsv files (and no other files!)", default="~/Programming/data/biobesu/vibe_versions/moon/_output_files/"),
  make_option(c("-c", "--cgd"), help="path to cgd .tsv file", default="~/Programming/data/biobesu/benchmark_data/CGD_2021-06-08.txt"),
  make_option(c("-o", "--output"), help="directory to write plots to", default="./")
);

# Configuration based on whether run through RStudio or through command line Rscript.
if(interactive()) {
  # Sets working directory to script dir.
  setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
} else {
  # Disables writing Rplots.pdf file when script is done.
  pdf(NULL)
}



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
ggSaveCustomWithPlot <- function(fileName, width, height, plot) {
  ggsave(paste0(params$output, fileName, ".pdf"), plot=plot, width=width, height=height)
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


########
# Name:
# getLog10Position
#
# Description:
# Calculates what value belongs to the given fraction for the input value when
# Using a log10-scale.
#
# Input:
# value - The value of which a fraction value should be calculated from.
# fraction - The fraction to use for calculation.
#
# Output:
# The fraction-value when using a log10 scale.
########
getLog10Position <- function(value, fraction) {
  return(10^(log10(value)*fraction))
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

# Load & filter cgd data.
cgdData <- read.table(params$cgd, header=T, sep="\t", colClasses=c("character"), comment.char = "", quote="")
cgdData <- cgdData$ENTREZ.GENE.ID

# Generates variables to store data in.
resultData <- list()
positionResults <- data.frame(matrix(nrow=nrow(benchmarkData)), row.names=benchmarkData$id)
totalResults <- data.frame(matrix(nrow=nrow(benchmarkData)), row.names=benchmarkData$id)

# Generate list of result files.
resultFiles <- list.files(params$results, full.names=TRUE)

# Checks whether limit of 6 files is reached.
stopifnot(length(resultFiles) <= 6)

# Digests all results.
for(resultFile in resultFiles) {
  fileName <- tail(strsplit(resultFile, '/')[[1]], n=1) # Removes path.
  version <- substr(fileName, 1, nchar(fileName)-4) # Removes '.tsv'
  resultData[[version]] <- sortRows(readResultFile(resultFile))
  positionResults[[version]] <- resultsPositionCalculator(benchmarkData, resultData[[version]])
  totalResults[[version]] <- calculateTotalGenesFound(resultData[[version]])
}
rm(resultFile, fileName, version)

# Removes initial empty matrix.
positionResults <- positionResults[,-1]
totalResults <- totalResults[,-1]

# Generate splitted genes for all tools: [[version]][[id]]@genes[[1]]
setClass("suggestedGenes", representation(genes="vector"))
resultOutputSplitted <- sapply(resultData, function(singleResultData) {
  sapply(rownames(singleResultData), function(id, singleResultData) {
    new("suggestedGenes", genes=strsplit(singleResultData[id,"suggested_genes"], ","))
  }, singleResultData=singleResultData)
}, simplify=FALSE)
names(resultOutputSplitted) <- names(resultData)

# Tool colors
if(length(resultData) > 2) {
  toolColors <- carto_pal(length(resultData), "Safe")
} else {
  toolColors <- carto_pal(3, "Safe")[1:length(resultData)]
}
names(toolColors) <- names(resultData)

##############################
########## FIGURE 1 ##########
##############################
### Scatterplot with means and missing

# Config.
xMax <- max(totalResults)
yMax <- max(positionResults, na.rm=TRUE)
labCols <- 2
xLabOptions <- rep(c(getLog10Position(xMax, 0.02),
                     getLog10Position(xMax, 0.4)), labCols)
yLabOptions <- c(rep(yMax, labCols),
                 rep(getLog10Position(yMax, 0.9), labCols),
                 rep(getLog10Position(yMax, 0.8), labCols),
                 rep(getLog10Position(yMax, 0.7), labCols))



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

gd$labX <- xLabOptions[1:length(resultData)]
gd$labY <- yLabOptions[1:length(resultData)]

# Plotting figure.
ggplot() +
  geom_point(data = posRelM, aes(x=total, y=rank, color=tool), size = 0.3) +
  geom_point(data = gd, aes(x=total, y=rank, fill=tool), shape = 21, color = "black", stroke = 1, size = 2) +
  # legend stuff
  geom_point(aes(x=getLog10Position(xMax, 0.05), y=getLog10Position(yMax, 0.2)), color = "black", size=0.3) +
  geom_text(aes(x=getLog10Position(xMax, 0.05), y=getLog10Position(yMax, 0.2), label = "= one causal gene"), color = "black", size = 2, hjust = 0, nudge_x = 0.1) +
  geom_point(aes(x=getLog10Position(xMax, 0.05), y=getLog10Position(yMax, 0.3)), shape = 1, color = "black", stroke = 1, size = 2) +
  geom_text(aes(x=getLog10Position(xMax, 0.05), y=getLog10Position(yMax, 0.3), label="= tool X and Y means"), color="black", hjust = 0, size = 2, nudge_x = 0.1) +
  geom_text(aes(x=getLog10Position(xMax, 0.02), y=getLog10Position(yMax, 0.05), label=paste0("Total: ", nrow(benchmarkData), "\ncausal genes")), color="black", hjust = 0, size = 2, nudge_x = 0.1) +
  geom_label(data = gd, aes(x = labX, y = labY, label  = NAs, fill = tool), color="white", hjust = 0, size = 2, fontface = "bold") +
  scale_y_log10(breaks = c(1, 10, 100, 1000, 10000)) + scale_x_log10(breaks = c(1, 10, 100, 1000, 10000, 40000)) +
  theme_bw() +
  theme(panel.grid = element_blank(), panel.border = element_rect(colour = "black"), axis.ticks = element_line(colour = "black"), legend.position = "none", axis.text = element_text(color = "black")) +
  scale_color_manual(values = toolColors) +
  scale_fill_manual(values = toolColors) +
  labs(x = "Total number of candidate genes returned", y = "Rank of the causal gene")

ggSaveCustom("fig1", width=4, height=2.5)

# Removes variables specific to this section.
rm(posRelM,totResM,gd,toolNaRanks)
