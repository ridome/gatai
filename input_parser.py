
import pandas as pd
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InputExcelParser:
    def parse(self, file_path):
        """
        Parses the Input Excel file and extracts task data.
        Returns a list of dicts: [{'task_name': '...', 'dates': {'date_col': val, ...}}]
        """
        logging.info(f"Parsing Input Excel: {file_path}")
        try:
            # Read Excel
            # header=0 implies first row is header.
            df = pd.read_excel(file_path, header=0)

            # Clean column names (strip whitespace)
            df.columns = df.columns.astype(str).str.strip()

            # Identify Task Column
            task_col = None
            for col in df.columns:
                if "任务" in col or "类别" in col:
                    task_col = col
                    break

            if not task_col:
                # Fallback: Assume the second column if "任务" not found, or first?
                # Image 1 had "数据类型" then "任务类别". So likely 2nd column.
                if len(df.columns) > 1:
                    task_col = df.columns[1]
                else:
                    task_col = df.columns[0]
                logging.warning(f"Could not explicitly identify 'Task' column. Defaulting to: {task_col}")

            # Identify Date Columns
            # Regex: digit dot digit [-] digit dot digit. e.g. 1.9-1.15
            # Or just broadly any column that looks like a date range.
            date_cols = []
            for col in df.columns:
                # Match "1.9-1.15" or "1.16-1.23"
                if re.search(r'\d+\.\d+-\d+\.\d+', col):
                    date_cols.append(col)

            logging.info(f"Identified Date Columns: {date_cols}")

            # Extract Data
            extracted_data = []
            for index, row in df.iterrows():
                task_name = str(row[task_col]).strip()

                # Skip empty or aggregate rows (often exist in reports)
                if not task_name or task_name.lower() == 'nan' or "总计" in task_name:
                    continue

                item = {
                    'task_name': task_name,
                    'dates': {}
                }

                for d_col in date_cols:
                    val = row[d_col]
                    # Handle NaN or empty
                    if pd.isna(val) or val == '':
                        val = 0

                    # Convert to string or keep as number?
                    # excel_manager expects values.
                    item['dates'][d_col] = str(val)

                extracted_data.append(item)

            return extracted_data

        except Exception as e:
            logging.error(f"Error parsing Excel: {e}")
            raise e

if __name__ == "__main__":
    # Test block
    # Create a dummy excel to test
    dummy_data = {
        '数据类型': ['A', 'B'],
        '任务类别': ['Task1', 'Task2'],
        '1.9-1.15': [100, 200],
        '1.16-1.23': [300, 400],
        '其它': ['x', 'y']
    }
    df = pd.DataFrame(dummy_data)
    df.to_excel("dummy_input.xlsx", index=False)

    parser = InputExcelParser()
    data = parser.parse("dummy_input.xlsx")
    print("Parsed Data:", data)
