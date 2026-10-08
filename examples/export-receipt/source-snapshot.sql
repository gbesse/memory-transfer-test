SELECT json_build_object(
  'bank_id', :'bank_id',
  'memory_units', COALESCE(
    json_agg(json_build_object(
      'id', id::text,
      'fact_type', fact_type,
      'source_memory_ids', source_memory_ids
    )),
    '[]'::json
  )
)
FROM memory_units
WHERE bank_id = :'bank_id';
