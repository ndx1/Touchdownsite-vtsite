-- 
-- PL/pgSQL Transaction example.
-- Update price to 60% of its value for any product "older" than January 1st, 2022.
--
do
$$
declare
-- Variables
	old_product record;
	old_date timestamptz := '2022-12-31 23:59:59+01';
	ratio FLOAT := 0.6;
	new_price numeric(10,2);
--
BEGIN
-- 	We look if we have any old products :
	IF EXISTS ( SELECT *
				FROM public.ventashop_product
				WHERE date_created < old_date ) THEN
--	 	If there are, we loop on them : 	
		for old_product in 
		  SELECT * FROM public.ventashop_product
			WHERE date_created < old_date
		loop 
			new_price = old_product.price * ratio;
--			We update the price field in the row :
			UPDATE public.vtshop_product
			set price = new_price
			WHERE id = old_product.id;
		end loop;
--		Validation.	
		COMMIT;
	ELSE
		ROLLBACK;
	END IF;
END;
$$
-- 
--