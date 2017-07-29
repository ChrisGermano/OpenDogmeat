import sys
import commentBreakdown as breakdown

if len(sys.argv) < 3:
    print "Insufficient params: [subreddit] [# of results]"
    sys.exit()

subreddit = sys.argv[1]
results = int(sys.argv[2])

breakdown.collect("s",subreddit,results)
