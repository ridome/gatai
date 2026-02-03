
import logging
from paddleocr import PaddleOCR
import pandas as pd
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OCRProcessor:
    def __init__(self):
        # Initialize PaddleOCR
        # use_angle_cls=True ensures text orientation is corrected
        # Removing show_log as it is not supported in this version
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')

    def process_image(self, image_path):
        """
        Processes the image and returns a structured list of tasks and their associated data.
        """
        logging.info(f"Processing image: {image_path}")
        # cls=True removed as it is causing issues in this version, and use_angle_cls=True in init should cover it
        result = self.ocr.ocr(image_path)

        if not result or not result[0]:
            logging.error("No text detected in image.")
            return []

        # Flatten the result structure
        boxes = [line[0] for line in result[0]]
        txts = [line[1][0] for line in result[0]]
        scores = [line[1][1] for line in result[0]]

        # Combine into a list of dicts for easier handling
        elements = []
        for box, txt, score in zip(boxes, txts, scores):
            # Calculate center y to group by rows
            center_y = (box[0][1] + box[2][1]) / 2
            center_x = (box[0][0] + box[1][0]) / 2
            elements.append({
                'text': txt,
                'box': box,
                'center_x': center_x,
                'center_y': center_y
            })

        # Group elements into rows based on Y-coordinate proximity
        rows = self._group_into_rows(elements)

        # Parse rows to identify headers and data
        parsed_data = self._parse_table_structure(rows)

        return parsed_data

    def _group_into_rows(self, elements, y_threshold=15):
        """
        Groups text elements into rows based on vertical proximity.
        """
        # Sort by Y first
        elements.sort(key=lambda x: x['center_y'])

        rows = []
        if not elements:
            return rows

        current_row = [elements[0]]

        for i in range(1, len(elements)):
            if abs(elements[i]['center_y'] - current_row[-1]['center_y']) < y_threshold:
                current_row.append(elements[i])
            else:
                current_row.sort(key=lambda x: x['center_x'])
                rows.append(current_row)
                current_row = [elements[i]]

        if current_row:
            current_row.sort(key=lambda x: x['center_x'])
            rows.append(current_row)

        return rows

    def _parse_table_structure(self, rows):
        """
        Identifies headers and extracts task data.
        """
        header_row_idx = -1
        headers = []

        # 1. Identify Header Row
        for idx, row in enumerate(rows):
            texts = [item['text'] for item in row]
            if any("任务" in t for t in texts) and any("数量" in t for t in texts):
                header_row_idx = idx
                headers = row
                logging.info(f"Header row found at index {idx}: {[t['text'] for t in headers]}")
                break

        if header_row_idx == -1:
            logging.error("Could not find table header row.")
            return []

        # 2. Analyze Columns (Date Columns)
        date_columns = []
        task_col_idx = -1

        for i, col in enumerate(headers):
            txt = col['text']
            if "任务" in txt or "类别" in txt:
                task_col_idx = i

            # Heuristic for date column
            if re.search(r'\d+\.\d+-\d+\.\d+', txt):
                date_columns.append((i, txt))
                logging.info(f"Identified Date Column: {txt} at index {i}")

        if task_col_idx == -1:
            if len(headers) > 1:
                task_col_idx = 1
            else:
                task_col_idx = 0
            logging.warning(f"Defaulting Task column to index {task_col_idx}")

        # 3. Extract Data Rows
        extracted_data = []

        for i in range(header_row_idx + 1, len(rows)):
            row = rows[i]
            if len(row) < 2:
                continue

            row_data = {}
            row_task_name = ""

            task_header = headers[task_col_idx]
            # Find item closest to task header
            closest_task_item = min(row, key=lambda x: abs(x['center_x'] - task_header['center_x']))

            if abs(closest_task_item['center_x'] - task_header['center_x']) < 200:
                row_task_name = closest_task_item['text']
            else:
                if len(row) > task_col_idx:
                     row_task_name = row[task_col_idx]['text']

            if not row_task_name:
                continue

            row_data['task_name'] = row_task_name
            row_data['dates'] = {}

            # Extract date values
            for date_idx, date_header_txt in date_columns:
                header_item = headers[date_idx]

                # Find the item in the current row closest to this header's X position
                # But filter only items that are to the right of task name? No, just absolute position.
                closest_val_item = min(row, key=lambda x: abs(x['center_x'] - header_item['center_x']))

                # If closest item is too far, assume empty or handled elsewhere
                # We need a stricter check because simply min() will always find something

                x_dist = abs(closest_val_item['center_x'] - header_item['center_x'])

                # If the item is closer to another date column, we shouldn't take it?
                # Actually, simply checking if it's "close enough" (e.g., < 50px) is usually fine for aligned tables
                if x_dist < 60:
                    row_data['dates'][date_header_txt] = closest_val_item['text']
                else:
                    row_data['dates'][date_header_txt] = "0" # Default to 0 or empty

            extracted_data.append(row_data)

        return extracted_data

if __name__ == "__main__":
    processor = OCRProcessor()
    data = processor.process_image("/tmp/file_attachments/image.png")
    print("Extracted Data:")
    for item in data:
        print(item)
