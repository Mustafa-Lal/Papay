import sys
from sqlalchemy import text
from app.database import engine

def main():
    if len(sys.argv) > 1:
        query_str = " ".join(sys.argv[1:])
    else:
        print("Enter your SQL query (press Enter twice to execute):")
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip() == "":
                break
            lines.append(line)
        query_str = " ".join(lines)

    if not query_str.strip():
        print("No query provided.")
        return

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query_str))
            
            # If it's a SELECT query, print the results
            if result.returns_rows:
                keys = result.keys()
                rows = result.fetchall()
                
                print(f"\n--- {len(rows)} Row(s) Returned ---")
                
                if not rows:
                    print("No results found.")
                    return

                # Very basic table formatting
                col_widths = [len(str(k)) for k in keys]
                for row in rows:
                    for i, val in enumerate(row):
                        col_widths[i] = max(col_widths[i], len(str(val)))
                
                header = " | ".join(str(k).ljust(w) for k, w in zip(keys, col_widths))
                print(header)
                print("-" * len(header))
                
                for row in rows:
                    print(" | ".join(str(v).ljust(w) for v, w in zip(row, col_widths)))
            else:
                conn.commit()
                print("\nQuery executed successfully. (No rows returned)")
                
    except Exception as e:
        print(f"\nError executing query: {e}")

if __name__ == "__main__":
    main()
