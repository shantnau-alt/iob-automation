import streamlit as st
from docxtpl import DocxTemplate
import io
import datetime
import os
import subprocess  # 🌟 Added for cloud/universal PDF rendering via LibreOffice
from num2words import num2words

# Page Configuration for a spacious, professional interface
st.set_page_config(page_title="IOB Loan Document Automation", layout="wide")

st.title("🏦 Indian Overseas Bank - Loan Document Automation System")
st.write("Select the corresponding workflow to generate complete, ready-to-print document packages.")

# Helper function to convert numeric currency into formal Indian English Word Notation
def currency_to_indian_words(number):
    try:
        words = num2words(number, lang='en_IN').title()
        words = words.replace("And", "and")
        return f"Rupees {words} Only"
    except Exception:
        return ""

# Main workflow router dropdown at the top
loan_type = st.selectbox("🎯 Choose Loan Type Workflow", ["🌾 Crop Loan (KCC)", "🎓 Education Loan"])

st.markdown("---")

# Global data structures initialization
context = {}
chosen_template = ""
validation_name = ""
validation_id = ""

# Setup layout columns
col1, col2 = st.columns(2)

# ==========================================
# FLOW A: CROP LOAN (KCC) CONFIGURATION
# ==========================================
if loan_type == "🌾 Crop Loan (KCC)":
    chosen_template = "templates/crop_loan_template.docx"
    
    with col1:
        st.subheader("👤 Borrower Information")
        customer_name = st.text_input("Customer Name (Mr/Mrs)", placeholder="e.g. Saroja")
        father_spouse = st.text_input("Father / Husband Name", placeholder="e.g. Perumal")
        mobile_number = st.text_input("Mobile Number", placeholder="e.g. 89259XXXXX")
        address = st.text_area("Full Address", placeholder="Door No, Street Name, Village, Pincode")

        st.subheader("🌾 Farm & Land Details")
        acre = st.text_input("Extent of Land (in Acres)", placeholder="e.g. 2.5")
        location = st.text_input("Location of Farm & Distance", placeholder="e.g. Kachirayapalayam, 2 KM")

    with col2:
        st.subheader("💰 KCC Account & Loan Details")
        loan_number = st.text_input("KCC Loan Account Number")
        sb_number = st.text_input("Savings Bank (SB) Account Number")
        since = st.text_input("SB Account Held Since (Year/Date)", placeholder="e.g. 2018")
        
        loan_amount = st.number_input("Loan Amount (Rs.)", min_value=0, step=5000, value=50000)
        calculated_words = currency_to_indian_words(loan_amount)
        amount_in_words = st.text_input("Amount in Words (Auto-generated)", value=calculated_words)
        
        icon_rating = st.text_input("ICON Rating", value="Satisfactory / High")

        st.subheader("📅 Dates Strategy")
        date = st.date_input("Document/Application Date", datetime.date.today())
        last_renewal_date = st.date_input("Last Renewal/Sanction Date", datetime.date.today() - datetime.timedelta(days=365))
        next_renewal_date = st.date_input("Next Due/Renewal Date", datetime.date.today() + datetime.timedelta(days=365))

    # Context Mapping tailored directly for the KCC Word Template architecture
    context = {
        'loan_number': loan_number, 'sb_number': sb_number, 'date': date.strftime("%d.%m.%Y"),
        'customer_name': customer_name, 'father_spouse': father_spouse, 'address': address,
        'mobile_number': mobile_number, 'acre': acre, 'location': location,
        'loan_amount': f"{loan_amount:,}", 'amount_in_words': amount_in_words,
        'last_renewal_date': last_renewal_date.strftime("%d.%m.%Y"),
        'next_renewal_date': next_renewal_date.strftime("%d.%m.%Y"),
        'since': since, 'icon_rating': icon_rating
    }
    validation_name = customer_name
    validation_id = loan_number

# ==========================================
# FLOW B: EDUCATION LOAN CONFIGURATION
# ==========================================
else:
    chosen_template = "templates/education_loan_template.docx"
    
    with col1:
        st.subheader("🎓 Student & Academic Details")
        student_name = st.text_input("Student Name", placeholder="e.g. Amit Kumar")
        parent_name = st.text_input("Father / Mother / Guardian Name", placeholder="e.g. Perumal")
        college_name = st.text_input("College / University Name", placeholder="e.g. Madras Medical College")
        course_name = st.text_input("Course Name", placeholder="e.g. B.Tech (IT), MBBS, MBA")
        academic_year = st.text_input("Academic Year Joined", placeholder="e.g. 2024-25")
        address = st.text_area("Permanent Address Details", placeholder="Door No, Street Name, Town, Pincode")

    with col2:
        st.subheader("💰 Financial Mapping & Subsidy Parameters")
        loan_amount = st.number_input("Sanctioned Loan Amount Limit (Rs.)", min_value=0, step=10000, value=200000)
        calculated_words = currency_to_indian_words(loan_amount)
        amount_in_words = st.text_input("Amount in Words (Auto-generated)", value=calculated_words)
        
        fee_paid = st.number_input("Seat Confirmation Fees Already Paid (Rs.)", min_value=0, step=1000, value=25000)
        sb_account_num = st.text_input("Savings Bank Account Number (for Reimbursement)")
        
        st.subheader("📅 Processing Context")
        date = st.date_input("Execution / Document Date", datetime.date.today())

    # Context Mapping matching the exact placeholder keys extracted from your Education Document layout
    context = {
        'date': date.strftime("%d.%m.%Y"),
        'student_name': student_name,
        'parent_name': parent_name,
        'address': address,
        'loan_amount': f"{loan_amount:,}",
        'course_name': course_name,
        'college_name': college_name,
        'fee_paid': f"{fee_paid:,}",
        'sb_account_num': sb_account_num,
        'amount_in_words': amount_in_words,
        'academic_year': academic_year
    }
    validation_name = student_name
    validation_id = sb_account_num

st.markdown("---")

# Setup clean binary memory target stream
word_buffer = io.BytesIO()

if st.button("🔥 Execute System Document Compilation", use_container_width=True):
    if not validation_name:
        st.error("❌ CRITICAL SETUP VALIDATION FAILED: Applicant Name cannot be left blank!")
    else:
        try:
            # Dynamically read out target file path structure based on drop-down context routing 
            doc = DocxTemplate(chosen_template)
            
            # Render fields into framework structure
            doc.render(context)
            doc.save(word_buffer)
            
            st.success(f"🎉 Success! Ready to extract print files for {validation_name}.")
            
            dl_col1, dl_col2 = st.columns(2)
            
            with dl_col1:
                st.download_button(
                    label="📥 Download Editable Word Document (.docx)",
                    data=word_buffer.getvalue(),
                    file_name=f"IOB_Document_{validation_name.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            
            with dl_col2:
                # 🌟 CLOUD & LINUX SECURE PDF ENGINE RENDERER (Bypasses win32com runtime crashes)
                temp_docx_path = f"temp_{validation_name.replace(' ', '_')}.docx"
                temp_pdf_path = f"temp_{validation_name.replace(' ', '_')}.pdf"
                
                with open(temp_docx_path, "wb") as f:
                    f.write(word_buffer.getvalue())
                
                try:
                    # Executes native headless office engine to compile binary clean PDFs effortlessly
                    subprocess.run([
                        "soffice", "--headless", "--convert-to", "pdf", temp_docx_path
                    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    with open(temp_pdf_path, "rb") as pdf_file:
                        pdf_data = pdf_file.read()
                    
                    st.download_button(
                        label="📄 Download Official Uneditable PDF (.pdf)",
                        data=pdf_data,
                        file_name=f"IOB_Document_{validation_name.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as docx_err:
                    st.info("💡 PDF Engine Notification: Document compiling successfully generated. Grab your editable Word file output directly whenever layout shifts are required!")
                finally:
                    # Systematic cleanup of ephemeral server staging copies
                    if os.path.exists(temp_docx_path): os.remove(temp_docx_path)
                    if os.path.exists(temp_pdf_path): os.remove(temp_pdf_path)
                    
        except FileNotFoundError:
            st.error(f"❌ TEMPLATE MISSING: Verify that '{chosen_template}' exists inside your templates folder directory.")
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")