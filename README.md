This GitHub repository contains the system files (main LLM API-call Python source code, Ollama structured output source code, LLM prompt system message, and LLM prompt user message 
developed and implemented in LLM API calling), and the derived evaluation data (gold-standard annotations and LLM outputs) related to the project
"Open-source large-language-model-based on-premises pipeline for automated data extraction from unstructured electronic health records: a pilot study".


A. Repository files

System files (located in main repository folder):
- ollama_llm_api_call_source_code.py (main LLM API-call Python source code)
- euroscore2_model_strict_grammar.py (Ollama structured output source code) 
- prompt.txt (LLM prompt system message)
- system.txt (LLM prompt user message)
- medical_reports.xlsx (medical reports file)

Derived evaluation data (located in folder: derived_evaluation_data):
- gold_standard_annotations.xlsx
- output_deepseek_r1_32b_qwen_distill_q4.xlsx
- output_deepseek_r1_32b_qwen_distill_q8.xlsx
- output_deepseek_r1_70b_llama_distill_q4.xlsx
- output_gemma3_27b_it_q4.xlsx
- output_gemma3_27b_it_q8.xlsx
- output_llama3.2_vision_90b_instruct_q4.xlsx
- output_llama3.3_70b_instruct_q4.xlsx
- output_qwen2.5vl_32b_q4.xlsx
- output_qwen2.5vl_32b_q8.xlsx
- output_qwen2.5vl_72b_q4.xlsx
- output_qwen3_30b_a3b_q4.xlsx
- output_qwen3_30b_a3b_q8.xlsx
- output_qwen3_32b_q4.xlsx
- output_qwen3_32b_q8.xlsx


B. Setup 

1. Download and place all system files in the same folder (WORKING_DIRECTORY)
2. Configure ollama_llm_api_call_source_code.py 
	- WORKDIR    = pathlib.Path(r"WORKING_DIRECTORY") -> Enter the path of the folder containing all system files (placeholder: WORKING_DIRECTORY).
	- OUTPUTDIR  = pathlib.Path(r"OUTPUT_DIRECTORY") -> Enter the path of the folder to save LLM output (placeholder: OUTPUT_DIRECTORY)
	- OLLAMA_URL = "LOCAL_OLLAMA_ENDPOINT_URL" -> Enter the URL of the local Ollama endpoint (placeholder: LOCAL_OLLAMA_ENDPOINT_URL)
	- MODEL      = "OLLAMA_LLM_NAME" -> Enter the Ollama LLM name (placeholder: OLLAMA_LLM_NAME)
3. Enter medical reports in the full_text column of medical_reports.xlsx (one cell per medical report)


C. Execution 

1. Execute ollama_llm_api_call_source_code.py
2. Based on the number of medical reports entered in medical_reports.xlsx, the size of the selected Ollama LLM, and the computing capacity of the system whereon the local Ollama endpoint is deployed
varying latency to LLM output can be expected. Upon completion the terminal returns a message with the number of medical reports for which a Pydantic-valid LLM-output has been returned.  
2. Check the OUTPUT_DIRECTORY path for .csv output. 
