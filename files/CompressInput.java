
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

class CompressInput {

	public static void main(String[] args) {

		System.out.println("Hello World");

		if (args.length != 1) {
			System.out.println("Arg error");
			return;
		}
		String workload = args[0];

		String input_file_name = "workload_" + workload + "_timing_a.json";
		FileReader file_reader;
		BufferedReader buffered_reader;
		String input_line = null;
		String final_string = "";
		String output_file_name = "workload_" + workload + "_single_line.txt";
		//String output_file_name = "bar.txt";
		FileWriter file_writer;
		BufferedWriter buffered_writer;
		int iteration = 0;
	
		try {
			file_reader = new FileReader(input_file_name);
			buffered_reader = new BufferedReader(file_reader);

			while (true) {
				input_line = buffered_reader.readLine();
				if (input_line == null) {
					break;
				}

				if (!input_line.contains("sql")) {
					input_line = input_line.replaceAll("\\s+", "");
					final_string = final_string + input_line;
				} else {
					final_string = final_string + input_line;
				}

				iteration++;
				if (iteration % 100 == 0) {
					System.out.println("Iteration:  " + iteration);
				}

			}

			file_reader.close();

			file_writer = new FileWriter(output_file_name);
			buffered_writer = new BufferedWriter(file_writer);
			buffered_writer.write(final_string);
			buffered_writer.close();

		} catch (IOException exception) {
			exception.printStackTrace();
			return;
		}



		return;

	}

}


