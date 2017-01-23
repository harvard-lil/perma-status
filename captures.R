library(tidyverse)

captures <- read_csv("./captures.csv")

ggplot(captures, aes(timestamp, y = capture_time, color = queue_time)) +
      geom_point(size = 0.1) +
      theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
      # http://stackoverflow.com/a/15625149/4074877
      geom_text(aes(label=ifelse(capture_time>200,as.character(guid),'')),hjust=0,vjust=0,size=2) +
      labs(y = 'capture time in seconds', color = 'queue time\nin seconds')

ggplot(captures, aes(timestamp, y = interval)) +
  geom_point(size = 0.1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  # http://stackoverflow.com/a/15625149/4074877
  geom_text(aes(label=ifelse(capture_time>200,as.character(guid),'')),hjust=0,vjust=0,size=2) +
  labs(y = 'interval to previous capture in seconds')

# need to plot mrc or mrcc / 20th capture ago, to see if
# proportion normally ever gets above say 0.3
#
# aha! it occasionally gets over 0.65, even (?) when there
# isn't a problem
withago <- captures %>%
  select(timestamp) %>%
  mutate(oneago = as.double(timestamp - lead(timestamp, 1),
                            units = "secs"),
         twentyago = as.double(timestamp - lead(timestamp, 20),
                               units = "secs"),
         agostat = oneago / twentyago)

max(withago$agostat, na.rm = TRUE)
# [1] 0.6588386
# but a subsequent capture gets
# [1] 0.9670425

ggplot(withago, mapping = aes(timestamp, agostat)) + geom_line()

