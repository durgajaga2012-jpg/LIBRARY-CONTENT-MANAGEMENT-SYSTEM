import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Library Management System", page_icon="📚", layout="wide")

st.title("📚 Library Management System")
st.markdown("Manage Books, Issue / Return to Students, Track Availability")

# ---------- Initialize Data in Session State ----------
if "books" not in st.session_state:
    st.session_state.books = [
        {"Book ID": "B001", "Title": "Python Programming", "Author": "Guido van Rossum", "Category": "Study", "Total": 5, "Available": 5},
        {"Book ID": "B002", "Title": "Ponniyin Selvan", "Author": "Kalki", "Category": "Novel", "Total": 3, "Available": 3},
        {"Book ID": "B003", "Title": "Harry Potter", "Author": "J.K. Rowling", "Category": "Story", "Total": 4, "Available": 4},
    ]

if "records" not in st.session_state:
    st.session_state.records = []  # Borrowing records

# ---------- Sidebar Menu ----------
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Add New Book", "Search Books", "Issue Book", "Return Book", "Student Records"])

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.subheader("📊 Dashboard")
    total_books = sum(b["Total"] for b in st.session_state.books)
    available_books = sum(b["Available"] for b in st.session_state.books)
    issued_books = total_books - available_books
    total_students = len(set(r["Student Name"] for r in st.session_state.records))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Book Titles", len(st.session_state.books))
    col2.metric("Total Copies", total_books)
    col3.metric("Available", available_books)
    col4.metric("Issued", issued_books)

    st.divider()
    st.subheader("📖 All Book Records")
    if st.session_state.books:
        df = pd.DataFrame(st.session_state.books)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No books found.")

# ---------- ADD NEW BOOK ----------
elif menu == "Add New Book":
    st.subheader("➕ Add New Book")
    with st.form("add_book_form"):
        book_id = st.text_input("Book ID (e.g. B004)")
        title = st.text_input("Book Title")
        author = st.text_input("Author Name")
        category = st.selectbox("Category", ["Study", "Novel", "Story", "Science", "History", "Other"])
        total = st.number_input("Total Copies", min_value=1, value=1)
        submitted = st.form_submit_button("Add Book")

        if submitted:
            if not book_id or not title or not author:
                st.error("Please fill all fields!")
            elif any(b["Book ID"] == book_id for b in st.session_state.books):
                st.error("Book ID already exists!")
            else:
                st.session_state.books.append({
                    "Book ID": book_id, "Title": title, "Author": author,
                    "Category": category, "Total": total, "Available": total
                })
                st.success(f"Book '{title}' Added Successfully!")

# ---------- SEARCH BOOKS ----------
elif menu == "Search Books":
    st.subheader("🔍 Search Books")
    search = st.text_input("Search by Title / Author / Category / Book ID")
    category_filter = st.selectbox("Filter by Category", ["All", "Study", "Novel", "Story", "Science", "History", "Other"])
    
    df = pd.DataFrame(st.session_state.books)
    if not df.empty:
        if search:
            df = df[df.apply(lambda row: search.lower() in str(row.values).lower(), axis=1)]
        if category_filter != "All":
            df = df[df["Category"] == category_filter]
        st.dataframe(df, use_container_width=True)
        st.write(f"Found {len(df)} books")
    else:
        st.info("No books available.")

# ---------- ISSUE BOOK ----------
elif menu == "Issue Book":
    st.subheader("📤 Issue Book to Student")
    
    available_books = [f"{b['Book ID']} - {b['Title']} (Avail: {b['Available']})" for b in st.session_state.books if b["Available"] > 0]
    
    if not available_books:
        st.warning("No books available to issue!")
    else:
        with st.form("issue_form"):
            selected = st.selectbox("Select Book", available_books)
            student_name = st.text_input("Student Name")
            student_id = st.text_input("Student ID / Roll No")
            issue_date = st.date_input("Issue Date", date.today())
            submit = st.form_submit_button("Issue Book")

            if submit:
                if not student_name or not student_id:
                    st.error("Please enter Student Name and ID!")
                else:
                    book_id = selected.split(" - ")[0]
                    for b in st.session_state.books:
                        if b["Book ID"] == book_id:
                            b["Available"] -= 1
                            break
                    st.session_state.records.append({
                        "Student Name": student_name,
                        "Student ID": student_id,
                        "Book ID": book_id,
                        "Book Title": selected.split(" - ")[1].split(" (Avail")[0],
                        "Issue Date": str(issue_date),
                        "Return Date": "-",
                        "Status": "Issued"
                    })
                    st.success(f"Book Issued to {student_name} Successfully!")

# ---------- RETURN BOOK ----------
elif menu == "Return Book":
    st.subheader("📥 Return Book")
    issued_records = [i for i, r in enumerate(st.session_state.records) if r["Status"] == "Issued"]
    
    if not issued_records:
        st.info("No issued books to return.")
    else:
        options = [f"{st.session_state.records[i]['Student Name']} - {st.session_state.records[i]['Book Title']} ({st.session_state.records[i]['Book ID']})" for i in issued_records]
        selected_idx = st.selectbox("Select Issued Book", range(len(options)), format_func=lambda x: options[x])
        return_date = st.date_input("Return Date", date.today())
        
        if st.button("Return Book"):
            record_index = issued_records[selected_idx]
            record = st.session_state.records[record_index]
            record["Status"] = "Returned"
            record["Return Date"] = str(return_date)
            # Increase availability
            for b in st.session_state.books:
                if b["Book ID"] == record["Book ID"]:
                    b["Available"] += 1
                    break
            st.success(f"Book '{record['Book Title']}' Returned by {record['Student Name']}!")

# ---------- STUDENT RECORDS ----------
elif menu == "Student Records":
    st.subheader("👨‍🎓 Student Borrowing Records")
    if st.session_state.records:
        df = pd.DataFrame(st.session_state.records)
        status_filter = st.selectbox("Filter by Status", ["All", "Issued", "Returned"])
        if status_filter != "All":
            df = df[df["Status"] == status_filter]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No borrowing records yet.")