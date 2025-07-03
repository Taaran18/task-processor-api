import uuid
from datetime import datetime
from employee import load_employee_data


def parse_structured_output(structured_output, choice, source_link=""):
    employee_data = load_employee_data()
    rows = []
    lines = structured_output.strip().split("\n")

    for line in lines:
        if line.strip() == "" or "---" in line:
            continue
        if "Task Description" in line and "Employee Name" in line:
            continue

        if any(d in line for d in ["|", "\t", ","]):
            if "|" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
            elif "\t" in line:
                parts = [p.strip() for p in line.split("\t") if p.strip()]
            else:
                parts = [p.strip() for p in line.split(",") if p.strip()]

            if len(parts) >= 9:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                task_id = uuid.uuid4().hex[:8]
                emp_name = parts[1]
                emp_email = employee_data.get(emp_name, "")
                assigned_name = parts[8]
                assigned_email = employee_data.get(assigned_name, "")
                row_data = [
                    now,
                    task_id,
                    parts[0],
                    emp_name,
                    emp_email,
                    parts[2],
                    parts[3],
                    parts[4],
                    parts[5],
                    parts[6],
                    assigned_name,
                    assigned_email,
                    parts[7],
                ]
                if choice in ["audio", "text"]:
                    matched_source = ""
                    if source_link:
                        for segment in source_link.strip().split("\n"):
                            if parts[0].lower() in segment.lower():
                                matched_source = segment.strip()
                                break
                    row_data.append(matched_source)


                rows.append(row_data)
    return rows
