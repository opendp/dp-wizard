column_name = COLUMN_NAME
print(
    f"DP counts for {column_name}, "
    f"assuming {contributions} contributions per individual"
)

groups = GROUP_NAMES
if groups:
    print(f"(grouped by {'/'.join(groups)})")

print(CONFIDENCE_NOTE, ACCURACY_NAME)
print(HISTOGRAM_NAME)
