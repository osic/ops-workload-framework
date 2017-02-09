import sys
class Calculate():
      def __init__(self):
          pass
      def getMin(self,time_list):
          x = min(float(i) for i in time_list)
          return x
      def getMax(self,time_list):
          x = max(float(i) for i in time_list)
          return x
      def getAverage(self, time_list):
          x = sum(time_list) / float(len(time_list))
          return x

