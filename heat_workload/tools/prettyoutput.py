from prettytable import PrettyTable
class Prettyoutput():
      def __init__(self,list_output):
          self.list_output = list_output
      def display(self):
          TABLE_LIST = []
          TOTAL_MIN = 0
          TOTAL_MAX = 0
          TOTAL_AVG = 0
          
          for dict in self.list_output:
              ROW_LIST = [0,0,0,0]
              for key,value in dict.iteritems():
                  if 'name' in key:
                     TASK_NAME = value
                     ROW_LIST[0] = TASK_NAME
                  elif 'min' in key:
                     TOTAL_MIN += value
                     value_min = value
                     ROW_LIST[1] = value
                  elif 'avg' in key:
                     TOTAL_AVG += value
                     value_avg = value
                     ROW_LIST[2] = value
                  elif 'max' in key:
                     TOTAL_MAX += value
                     value_max = value
                     ROW_LIST[3] = value
              TABLE_LIST.append(ROW_LIST)
          x = PrettyTable(["Task Name", "Minimum Time (seconds)", "Average Time (seconds)", "Maximum Time (seconds)"])
          for row in TABLE_LIST:
              x.add_row(row)
          x.add_row(["TOTAL", TOTAL_MIN, TOTAL_AVG, TOTAL_MAX])
          print x
