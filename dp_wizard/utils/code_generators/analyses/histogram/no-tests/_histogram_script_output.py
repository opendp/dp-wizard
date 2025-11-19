column_name = COLUMN_NAME
print(
    f"DP counts for {column_name}, assuming {contributions} contributions per individual"  # noqa: B950
)

group_names = GROUP_NAMES
if group_names:
    print(f"(grouped by {'/'.join(group_names)})")

print(CONFIDENCE_NOTE, ACCURACY_NAME)
print(HISTOGRAM_NAME)
