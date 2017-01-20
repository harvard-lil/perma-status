library(tidyverse)

captures <- read_csv("/Users/bsteinberg/Documents/analytics/captures.csv")

ggplot(captures, aes(timestamp, y = capture_time, color = queue_time)) + 
      geom_point(size = 0.1) + 
      theme(axis.text.x = element_text(angle = 45, hjust = 1)) + 
      # http://stackoverflow.com/a/15625149/4074877
      geom_text(aes(label=ifelse(capture_time>200,as.character(guid),'')),hjust=0,vjust=0,size=2) +
      labs(y = 'capture time in seconds', color = 'queue time\nin seconds')

