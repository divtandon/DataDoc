Generate a {target} for the dataset `{table}`.

Steps:
1. Look up `{table}` in DataHub: schema (columns + types + descriptions),
   upstream/downstream lineage, owners, and any glossary terms or tags.
2. Use that real context to write the {target}. Reference actual column
   names — do not invent any.
3. Write the result to `{out_path}` using the write_file tool.
4. If you find undocumented columns or likely PII you're confident about,
   tag or describe them back in DataHub.

Additional instructions from the caller: {extra_instructions}
