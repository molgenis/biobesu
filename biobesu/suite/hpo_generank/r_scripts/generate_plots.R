########
# Name:
# generate_plots.R
#
# Description:
# Generates plots for this biobesu benchmark suite.
#
# Important:
# Script automatically loads all files given within the directory given through the `--results` option.
# Be sure this directory only contains result .tsv files and not more than 6 of these!
# When running Biobesu, these files need to be collected from their individual output directories first.
# 
# When running through RStudio:
# Ensure all `default` values in `options` are adjusted to their correct paths before running.
#
# When running through the command line (Rscript):
# Rscript generate_plots.R -b benchmark_data.tsv -r benchmark_results/ -c CGD_2021-06-08.txt -o ./plots/
# OR
# Prepare as described for RStudio, `cd` to directory of this script and run `Rscript`.
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
  make_option(c("-b", "--benchmark"), help="path to benchmark .tsv file", default="~/Programming/data/biobesu/benchmark_data/benchmark_data-ncbi_id.tsv"),
  make_option(c("-r", "--results"), help="directory containing the benchmark result .tsv files (and no other files!)", default="~/Programming/data/biobesu/hpo_generank/paper/_to_plot"),
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
#stopifnot(length(resultFiles) <= 6)

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
xLabOptions <- c(rep(c(getLog10Position(xMax, 0.02),
                     getLog10Position(xMax, 0.4)), 3),
                 rep(getLog10Position(xMax, 0.02), 4))
yLabOptions <- c(rep(yMax, 2),
                 rep(getLog10Position(yMax, 0.9), labCols),
                 rep(getLog10Position(yMax, 0.8), labCols),
                 getLog10Position(yMax, 0.7),
                 getLog10Position(yMax, 0.6),
                 getLog10Position(yMax, 0.5),
                 getLog10Position(yMax, 0.4))



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



##############################
########## FIGURE 3 ##########
##############################
### Analysis to show practical value.

# Defines number of runs.
runs <- 25

# Defines number of spiking genes.
nSpikingGenes <- 19

# Set seed for pseudo-random numbers for reproducibility.
# Don't forget to reset seed when re-running code!!!
set.seed(0)

# Runs benchmark a number of times.
enrichedScores <- sapply(1:runs, function(x, nSpikingGenes) {
  # Generate sample matrix containing the genes to use for ranking (excluding the target gene).
  cgdSample <- t(apply(benchmarkData, 1, function(case, nSpikingGenes) {
    # Select all CGD genes minus the current causal one.
    cgdMinusCurrentGene <- cgdData[!cgdData %in% case["gene_id"]]
    # Randomly sample 19 other genes.
    cgdSample <- sample(cgdMinusCurrentGene, nSpikingGenes)
  }, nSpikingGenes=nSpikingGenes))
  
  # Goes through all cases.
  runScores <- t(sapply(1:nrow(benchmarkData), function(nRow, benchmarkData, cgdSample, resultOutputSplitted) {
    # Defines the target gene.
    benchmarkGene <- benchmarkData[nRow,"gene_id"]
    # Defines the full set of genes which need to be ranked (target + cgdSample).
    geneSet <- c(benchmarkGene, cgdSample[nRow,])
    
    # Goes through all result sets.
    sapply(names(resultOutputSplitted), function(resultSetName, id, benchmarkGene, geneSet, resultOutputSplitted) {
      # Finds matches for the enriched gene set within the full output for that resultSet/id 
      geneSetMatches <- match(geneSet, resultOutputSplitted[[resultSetName]][[id]]@genes[[1]])
      # If benchmark gene is not found, returns adjusted score.
      if(is.na(geneSetMatches[1])){
        #return(mean(c(sum(!is.na(geneSetMatches)), length(geneSet)))) # method 1: missing rank middle of input set minus outsize, realistic
        #return(length(geneSet)) # method 2: input set size, pessimistic, plot will spike at very end
        #return(NA) # method 3: harsh: missing genes do NOT increase the cumulative hits, some lines go flat
        return(sample(sum(!is.na(geneSetMatches)):length(geneSet), 1)) # method 4: missing rank at random position of input set minus outsize, super realistic
      }
      # Orders the found matches (NA=LAST).
      geneSetOrdered <- geneSet[order(geneSetMatches)]
      # Returns the found location of the target gene in the enriched gene set.
      return(match(benchmarkGene, geneSetOrdered))
    }, id=benchmarkData[nRow,"id"], benchmarkGene=benchmarkGene, geneSet=geneSet, resultOutputSplitted=resultOutputSplitted)
  }, benchmarkData=benchmarkData, cgdSample=cgdSample, resultOutputSplitted=resultOutputSplitted))
  
  # Renames rows to their id.
  rownames(runScores) <- benchmarkData$id
  # Returns scores for each resultSet for a single run.
  return(runScores)
}, nSpikingGenes=nSpikingGenes, simplify=FALSE)

# Calculate median per tool/case combination.
medianScores <- matrix(sapply(1:length(enrichedScores[[1]]), function(x) {
  median(sapply(enrichedScores, "[[", x))
}), ncol=ncol(positionResults), dimnames=list(benchmarkData$id, names(resultData)))

# Genes found per cutoff.
foundPerCutoff <- sapply(1:(nSpikingGenes+1), function(x) {
  apply(medianScores <= x,2,sum, na.rm=TRUE)
})
colnames(foundPerCutoff) <- 1:(nSpikingGenes+1)

# Plot preparations.
melted <- melt(t(foundPerCutoff))
colnames(melted) <- c("cutoff", "tool", "value")

# Plot configuration.
xScaleMax <- ncol(foundPerCutoff)
yScaleMin <- round_any(min(foundPerCutoff), 5, floor)
yScaleMax <- round_any(max(foundPerCutoff), 5, ceiling)
yScaleSteps <- max(5, round_any((yScaleMax - yScaleMin) / 6, 5))

# Plot figure.
ggplot() +
  geom_line(data = melted, aes(x = cutoff, y = value, color = tool), size=1) +
  geom_point(data = melted, aes(x = cutoff, y = value, color = tool), size=3) +
  scale_color_manual(values = toolColors) +
  scale_x_continuous(breaks = seq(1,xScaleMax,1), limits = c(1,xScaleMax)) +
  scale_y_continuous(limits=c(yScaleMin, yScaleMax), breaks = seq(yScaleMin,yScaleMax,yScaleSteps)) +
  theme(text = element_text(size=20), legend.title=element_blank(), legend.position = c(0.7, 0.45),
        panel.background = element_blank(), legend.key = element_blank(), legend.background = element_blank(),
        legend.text = element_text(size=12), legend.key.width = unit(2, "cm"), legend.key.height = unit(1, "cm")) +
  labs(x = "Gene rank in simulated spiked-in clinical gene sets", y = "Cumul. nr. of causal genes detected")
grid.ls(grid.force())
grid.gedit("key-[0-9]*-1-2", size = unit(8, "mm"))
myPlot <- (grid.grab())
ggSaveCustomWithPlot("fig3", width=8, height=5, plot=myPlot)


# Removes variables specific to this section.
rm(runs,nSpikingGenes,enrichedScores,medianScores,foundPerCutoff,melted)
