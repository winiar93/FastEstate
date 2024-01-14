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
	updated_at,
  offer_url,
  street,
    (total_price - min_price) / (max_price - min_price) AS normalized_total_price,
    (area_square_meters - min_area) / (max_area - min_area) AS normalized_area,
    CASE
	-- individually provided weights
	WHEN rooms_number = 1 THEN 0.2
    WHEN rooms_number = 2 THEN 0.6
    WHEN rooms_number = 3 THEN 1
    WHEN rooms_number = 4 THEN 1
    when rooms_number = 5 THEN 0.2
    when rooms_number = 6 THEN 0.2
    END AS normalized_rooms_number
  FROM
    public.flat_offers
  CROSS JOIN
    min_max_prices
  CROSS JOIN
    min_max_areas
),

flats_rank as (select
offer_id,
1 - normalized_total_price + normalized_area + normalized_rooms_number as ranking
FROM
normalized_values
where updated_at::date = NOW()::date)


UPDATE public.flat_offers
SET "rank" = flats_rank.ranking
FROM flats_rank
WHERE public.flat_offers.offer_id = flats_rank.offer_id;

delete from public.flat_offers
where "rank" is Null