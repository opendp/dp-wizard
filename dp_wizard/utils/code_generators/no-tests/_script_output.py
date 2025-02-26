column_name = COLUMN_NAME
print(
    f"DP counts for {column_name}, "
    f"assuming {contributions} contributions per individual"
)

group_names = GROUP_NAMES
if group_names:
    print(f"(grouped by {'/'.join(group_names)})")

print(CONFIDENCE_NOTE, ACCURACY_NAME)
print(HISTOGRAM_NAME)
