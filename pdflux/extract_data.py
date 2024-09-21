import  aspose.cells 
from aspose.cells import Workbook

workbook = Workbook("/data/shenyuge/pdflux/2024-04-03：贵州茅台：贵州茅台2023年年度报告.xls")
# workbook.combine(Workbook("Combine.xlsx"))
workbook.save("/data/shenyuge/pdflux/output.json")