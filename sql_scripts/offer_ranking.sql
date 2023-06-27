
 WITH min_max_prices AS (
  SELECT
    MIN(total_price) AS min_price,
    MAX(total_price) AS max_price
  FROM
    public.flat_offers
),
min_max_areas AS (
  SELECT
    MIN(area_square_meters) AS min_area,
    MAX(area_square_meters) AS max_area
  FROM
    public.flat_offers
),
normalized_values AS (
  select
    offer_id,
  offer_url,
  street,
    (total_price - min_price) / (max_price - min_price) AS normalized_total_price,
    (area_square_meters - min_area) / (max_area - min_area) AS normalized_area,
    CASE
	WHEN rooms_number = 'ONE' THEN 0.1
    WHEN rooms_number = 'TWO' THEN 0.2
    WHEN rooms_number = 'THREE' THEN 0.3
    WHEN rooms_number = 'FOUR' THEN 0.4
    when rooms_number = 'FIVE' THEN 0.5
    END AS normalized_rooms_number
  FROM
    public.flat_offers
  CROSS JOIN
    min_max_prices
  CROSS JOIN
    min_max_areas
)
select
  offer_id,
  offer_url,
  street,
  1 - normalized_total_price as normalized_total_price,
  normalized_area,
  normalized_rooms_number,
  1 - normalized_total_price + normalized_area + normalized_rooms_number as ranking
 
FROM
  normalized_values;
 
 