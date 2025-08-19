# Candidate Task Sheet: Build an ADGM-Compliant Corporate Agent with Document Intelligence 

## 1. Task Overview 

As part of the evaluation process, you are required to build an intelligent AI-powered legal assistant called the Corporate Agent . This agent will assist in reviewing, validat-ing, and helping users prepare documentation for business incorporation and compliance within the Abu Dhabi Global Market (ADGM) jurisdiction. 

Key Capabilities: The agent must accept uploaded legal documents (in ‘.docx‘ format), verify completeness of submissions based on ADGM rules, highlight red flags, insert contextual comments, and generate a reviewed, downloadable version of the file. It should also inform users if required documents are missing based on a pre-defined checklist. You are also provided with official ADGM links and a reference document. You must apply RAG (Retrieval-Augmented Generation) to ensure your system aligns with real-world ADGM laws, regulations, and processes. 

## 2. Functional Objectives 

Your Corporate Agent should be able to: 1. Accept ‘.docx‘ documents uploaded by the user. 2. Parse the uploaded documents and identify document types. 3. Check if all mandatory documents are present for specific legal processes (e.g., company incorporation). 4. Detect legal red flags and inconsistencies within each document. 5. Insert contextual comments in the ‘.docx‘ file for flagged content. 6. Provide legally compliant clause suggestions (optional). 7. Output a downloadable marked-up ‘.docx‘ file. 8. Generate a structured JSON/Python report summarizing the findings. 13. New Feature: Document Checklist Verification 

Your agent must also: 

• Automatically recognize which legal process the user is attempting (e.g., incorpo-ration, licensing, etc.). 

• Compare uploaded documents against the required ADGM checklist. 

• Notify the user if any mandatory document is missing. 

• Example: For Company Incorporation, if only 4 of the 5 required documents are uploaded, the agent should respond: “It appears that you’re trying to incorporate a company in ADGM. Based on our reference list, you have uploaded 4 out of 5 required documents. The missing document appears to be: ‘Register of Members and Direc-tors’.” 

## 4. Technical Requirements 

• Use Gradio (or Streamlit) for UI demonstration. No frontend design required. 

• Use any RAG-compatible LLM (Gemini,OpenAI, Ollama, Claude, etc.). 

• Inputs: ‘.docx‘ documents 

• Outputs: 

– Reviewed ‘.docx‘ file with highlights/comments 

– Structured JSON or Python dictionary summarizing analysis 

• Must use RAG with the provided ADGM reference documents and links for legal accuracy. 

## 5. Document Types and Use Cases 

Your agent should handle at least the following categories of documents: 

5.1 Company Formation Documents 

• Articles of Association (AoA) 

• Memorandum of Association (MoA/MoU) 

• Board Resolution Templates 

• Shareholder Resolution Templates 

• Incorporation Application Form 

• UBO Declaration Form 

• Register of Members and Directors 

• Change of Registered Address Notice 

5.2 Other Categories (Check attached files) 

- Licensing Regulatory Filings - Employment HR Contracts - Commercial Agreements - Compliance Risk Policies 26. Red Flag Detection Features 

• Invalid or missing clauses 

• Incorrect jurisdiction (e.g., referencing UAE Federal Courts instead of ADGM) 

• Ambiguous or non-binding language 

• Missing signatory sections or improper formatting 

• Non-compliance with ADGM-specific templates 

## 7. Inline Commenting Suggestions 

• Insert comments inside the ‘.docx‘ file at relevant locations. 

• Cite the exact ADGM law or rule that applies (e.g., “Per ADGM Companies Reg-ulations 2020, Art. 6...”) 

• (Optional) Offer alternative clause wording for common issues. 

## 8. Output Format (Example) 

In addition to the ‘.docx‘ file, return a structured output: 

{"process": "Company Incorporation", "documents_uploaded": 4, "required_documents": 5, "missing_document": "Register of Members and Directors", "issues_found": [ {"document": "Articles of Association", "section": "Clause 3.1", "issue": "Jurisdiction clause does not specify ADGM", "severity": "High", "suggestion": "Update jurisdiction to ADGM Courts." }]}

## 9. Submission Checklist 

Please submit the following: 

• GitHub repository link or zipped codebase 

• README with setup instructions 

• One example document (.docx) before and after review 3• Generated structured output file (JSON or Python dict) 

• Screenshot or demo video 

## 11. Attached Files Resources 

• Reference Document: “Document Upload Categories” 

• Legal Data Sources For any questions or clarifications, feel free to reach out. Best of luck! – Team Valura 

4
