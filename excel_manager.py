
import logging
import os
import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ExcelManager:
    def __init__(self, excel_path):
        self.file_path = excel_path
        # Define the structure based on "Image 2" (Target)
        # Groups: 图框类, 图片文本, 视频文本, 文本对, 语音类
        # Columns: 任务类别, 优先级, 任务类别(Sub), 状态, 支撑任务, 未来标注数量, 本期数量, 已标数据总量...
        # We need a standard mapping for the header structure.
        self.standard_columns = [
            "Group",          # Derived or Manual (e.g., 图框类) - Column A effectively
            "Priority",       # 优先级
            "Task Name",      # 任务类别
            "Status",         # 状态
            "Support Task",   # 支撑任务
            "Future Qty",     # 未来标注数量
            "Current Qty",    # 本期数量 (From Image 1 '预计数量'?)
            "Total Labeled",  # 已标数据总量
            "Weekly Capacity",# 最新周产能
            "Total Data",     # 本期数据总量
            "PH", "CN", "Completion", "Time Needed"
        ]

    def update_or_create(self, data):
        """
        data: List of dicts, e.g. [{'task_name': '文搜图', 'dates': {'1.9-1.15': '2280', ...}}, ...]
        """
        if os.path.exists(self.file_path):
            self._update_existing_excel(data)
        else:
            self._create_new_excel(data)

    def _create_new_excel(self, data):
        logging.info(f"Creating new Excel file: {self.file_path}")
        wb = Workbook()
        ws = wb.active
        ws.title = "Task Tracker"

        # 1. Setup Headers
        # Standard columns first
        headers = self.standard_columns.copy()

        # Collect all dynamic date columns from data
        all_dates = set()
        for item in data:
            if 'dates' in item:
                all_dates.update(item['dates'].keys())

        # Sort dates if possible, otherwise just sorted list
        sorted_dates = sorted(list(all_dates))
        headers.extend(sorted_dates)

        # Write Header
        ws.append(headers)

        # 2. Populate Data
        for item in data:
            row = [""] * len(headers)

            # Fill Task Name (Index 2 based on standard_columns)
            # "Group" is 0, "Priority" is 1, "Task Name" is 2
            row[2] = item.get('task_name', '')

            # Fill default values or mapped values?
            # Image 1 '预计数量' might map to 'Current Qty' (Index 6) or just be ignored?
            # The prompt said "Image 1 date columns are added as new columns".
            # It didn't specify where '预计数量' goes. I'll assume it goes to "Future Qty" or "Current Qty".
            # Let's check Image 1 columns again: "预计数量", dates, "已标注总量", "进度".
            # "已标注总量" -> "Total Labeled" (Index 7)
            # Let's try to map if keys exist in item (OCR might capture them if I improve OCR to capture non-date cols)
            # Currently OCR only returns 'task_name' and 'dates'.
            # I should update OCR to capture '预计数量' and '已标注总量' if possible, but let's stick to dates for now as requested.

            # Fill Dates
            for date_key, value in item.get('dates', {}).items():
                if date_key in headers:
                    col_idx = headers.index(date_key)
                    row[col_idx] = value

            ws.append(row)

        wb.save(self.file_path)
        logging.info("New Excel created successfully.")

    def _update_existing_excel(self, data):
        logging.info(f"Updating existing Excel file: {self.file_path}")
        wb = load_workbook(self.file_path)
        ws = wb.active

        # Get existing headers
        existing_headers = [cell.value for cell in ws[1]]

        # Identify new date columns
        all_new_dates = set()
        for item in data:
            if 'dates' in item:
                all_new_dates.update(item['dates'].keys())

        new_columns = [d for d in sorted(list(all_new_dates)) if d not in existing_headers]

        # Add new columns to header
        start_col = len(existing_headers) + 1
        for i, new_col in enumerate(new_columns):
            ws.cell(row=1, column=start_col + i, value=new_col)
            existing_headers.append(new_col)

        # Update Rows
        # Map Task Name to Row Index
        # Assuming Task Name is in a specific column. In my create logic it is index 2 (Column C).
        # We need to scan the sheet to find the Task Name column.
        # Heuristic: Find column named "Task Name" or "任务类别"
        task_col_idx = -1
        for idx, h in enumerate(existing_headers):
            if h and ("Task Name" in str(h) or "任务类别" in str(h)):
                task_col_idx = idx + 1 # 1-based
                break

        if task_col_idx == -1:
            # Fallback to column C (3)
            task_col_idx = 3

        # Build map of existing tasks {Name: RowIndex}
        existing_tasks = {}
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            # values_only=True returns tuple.
            task_name = row[task_col_idx - 1] # 0-based tuple access
            if task_name:
                existing_tasks[str(task_name).strip()] = row_idx

        # Process Input Data
        for item in data:
            task_name = item.get('task_name', '').strip()
            if not task_name:
                continue

            row_index = existing_tasks.get(task_name)

            if row_index:
                # Update existing row
                logging.info(f"Updating task: {task_name} at row {row_index}")
                self._fill_row_dates(ws, row_index, existing_headers, item['dates'])
            else:
                # Append new row
                logging.info(f"Adding new task: {task_name}")
                new_row_idx = ws.max_row + 1
                ws.cell(row=new_row_idx, column=task_col_idx, value=task_name)
                # Set Group to "New" or Uncategorized?
                # ws.cell(row=new_row_idx, column=1, value="Uncategorized")
                self._fill_row_dates(ws, new_row_idx, existing_headers, item['dates'])
                existing_tasks[task_name] = new_row_idx # Update map just in case duplicates in input

        wb.save(self.file_path)
        logging.info("Excel updated successfully.")

    def _fill_row_dates(self, ws, row_idx, headers, dates_dict):
        for date_key, value in dates_dict.items():
            if date_key in headers:
                col_idx = headers.index(date_key) + 1 # 1-based
                ws.cell(row=row_idx, column=col_idx, value=float(value) if value.replace('.','',1).isdigit() else value)

if __name__ == "__main__":
    # Test Block with Mock Data
    mock_data = [
        {'task_name': '文搜图', 'dates': {'1.9-1.15': '2280', '1.16-1.23': '3120'}},
        {'task_name': 'New Task X', 'dates': {'1.9-1.15': '100', '1.26-29': '500'}}
    ]

    manager = ExcelManager("test_output.xlsx")
    # First Run - Create
    manager.update_or_create(mock_data)

    # Second Run - Update with new column
    mock_data_2 = [
        {'task_name': '文搜图', 'dates': {'2.1-2.7': '4000'}},
        {'task_name': 'Another Task', 'dates': {'2.1-2.7': '10'}}
    ]
    manager.update_or_create(mock_data_2)
    print("Test complete. Check test_output.xlsx")
