import argparse
import os
from datetime import datetime
from multiprocessing import Pool, Manager

from utils import initialize_excel, get_timestamp
from capture import take_screenshot
from merge import merge_png_to_pdf


# Main function
def main(start_question, end_question, num_processes):
    # Initialize Excel
    workbook, sheet = initialize_excel()

    # Get the current timestamp
    timestamp = get_timestamp()

    # Create output directory with question range and timestamp
    output_dir = os.path.join("./outputs", f"{start_question}_{end_question}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    # Create subdirectory for PNG files
    png_output_dir = os.path.join(output_dir, f"{start_question}_{end_question}_{timestamp}_pngs")
    os.makedirs(png_output_dir, exist_ok=True)

    # Use Manager to handle shared results list
    with Manager() as manager:
        results = manager.list()

        # Create a pool of processes
        with Pool(processes=num_processes) as pool:
            tasks = [(question_number, timestamp, png_output_dir, results) for question_number in range(start_question, end_question + 1)]
            pool.starmap(take_screenshot, tasks)

        # Sort results by question number to maintain order
        sorted_results = sorted(results, key=lambda x: x[0])

        # Process results
        screenshot_filenames = []
        for result in sorted_results:
            question_number, query, current_url, screenshot_filename = result
            if query and current_url and screenshot_filename:
                sheet.append([question_number, query, current_url])
                screenshot_filenames.append(screenshot_filename)

        # Save the Excel workbook with timestamp and question range
        excel_filename = os.path.join(
            output_dir,
            f"queries_and_links_{start_question}_to_{end_question}_{timestamp}.xlsx",
        )
        workbook.save(excel_filename)
        print(f"Excel file saved as '{excel_filename}'")

        # Merge PNG files into a PDF
        pdf_filename = os.path.join(
            output_dir, f"screenshots_{start_question}_to_{end_question}_{timestamp}.pdf"
        )
        screenshot_paths = [
            os.path.join(png_output_dir, filename) for filename in screenshot_filenames
        ]
        merge_png_to_pdf(screenshot_paths, pdf_filename)

    print("All processes completed.")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Take screenshots of Google search results and save them to an Excel file and PDF."
    )
    parser.add_argument("start_question", type=int, help="The starting question number")
    parser.add_argument("end_question", type=int, help="The ending question number")
    parser.add_argument("--num_processes", type=int, default=4, help="The number of processes to use")
    args = parser.parse_args()

    # Run the main function with the provided arguments
    main(args.start_question, args.end_question, args.num_processes)
