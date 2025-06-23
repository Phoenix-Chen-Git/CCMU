# Load required libraries
dir.create("~/Rlibs", showWarnings = FALSE)
install.packages("stringr", lib = "~/Rlibs")
dir.create("~/Rlibs", showWarnings = FALSE)
install.packages("crisprScore", lib = "~/Rlibs")

library(stringr)
library(crisprScore)
# Get command line arguments
args <- commandArgs(trailingOnly = TRUE)
input <- args[1]

# Extract spacer (first 20 characters)
spacer <- substr(input, 1, 20)

# Set the path to the directory
csv_dir <- "split_by_seq/"

# Get a list of all CSV files in the directory
csv_files <- list.files(path = csv_dir, pattern = "\\.csv$", full.names = TRUE)

# Iterate over and process each CSV file
for (csv in csv_files) {
  data <- read.csv(csv)

  # Assume 'target' column exists
  if (!"target" %in% colnames(data)) {
    cat("Skipping", csv, ": no 'target' column found\n")
    next
  }

  targets <- as.character(data$target)
  protospacers <- substr(targets, 1, 20)
  pams <- substr(targets, nchar(targets) - 2 + 1, nchar(targets))

  current_csv_CFD <- getCFDScores(spacers = spacer,
                                  protospacers = protospacers,
                                  pams = pams)

  print(paste("Processed:", csv))
  print(current_csv_CFD)
}
