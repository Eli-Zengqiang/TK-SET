import sys
import math

import getopt
def cacl_result(x,y):
    sum=x + int(y)
    print(sum)

if __name__=="__main__":
    # try:
    #
    #     if len(sys.argv)> 1:
    #         x = int(sys.argv[1])
    #         y = int(sys.argv[2])
    #         cacl_result(x,y)
    #
    # except:
    #     pass

    ###########有选项的格式##########################
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:n:")

    except:
        pass

    for opt,arg in opts:
        if opt in ("-h","--h"):
            x= int(arg)
        elif opt == "-n":
            y = int(arg)
        else:
            y=0
    cacl_result(x,y)



