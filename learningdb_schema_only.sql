

SELECT pg_catalog.set_config('search_path', '', false);

CREATE FUNCTION public.auto_add_after_insert_func() RETURNS trigger
    LANGUAGE plpgsql
    AS $_$
declare
	day_table TEXT;
	day_tables TEXT[] := array['Day_2', 'Day_4','Day_7','Day_12','Day_21'];
	day_offset INT;
begin
	foreach day_table in array day_tables loop
		day_offset := CAST(regexp_replace(day_table, '\D', '','g') as INT);
		execute format('
						insert into "%s"("ID", "Word", "Meaning", "Example in French", "Example in English", "Deadline") 
						values ($1, $2, $3, $4, $5, $6)
						', day_table)

		Using 
			NEW."ID", 
			NEW."Word", 
			NEW."Meaning", 
			NEW."Example in French", 
			NEW."Example in English", 
			NEW."Start date" + (day_offset - 1 || ' days')::interval;
	end loop;
	return NEW;
end;
$_$;

ALTER FUNCTION public.auto_add_after_insert_func() OWNER TO postgres;

CREATE FUNCTION public.auto_change_date_after_update_func() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
Declare 
	deadline TEXT;
	deadlines TEXT[] := Array['Day_2', 'Day_4','Day_7','Day_12','Day_21'];
	day_offset INT;
begin
	foreach deadline in array deadlines loop
		day_offset := CAST(regexp_replace(deadline, '\D', '','g') as INT);
		execute format(
						'Update %I SET "Deadline" = %L where "ID" = %L;', 
						deadline,
						NEW."Start date" + (day_offset - 1)*INTERVAL '1 day',
						NEW."ID"
						);
	end loop;
	return NEW;
end;
$$;

ALTER FUNCTION public.auto_change_date_after_update_func() OWNER TO postgres;

CREATE TABLE public."Day_12" (
    "ID" integer NOT NULL,
    "Word" text,
    "Meaning" text,
    "Example in French" text,
    "Example in English" text,
    "Deadline" date
);

ALTER TABLE public."Day_12" OWNER TO postgres;

CREATE TABLE public."Day_2" (
    "ID" integer NOT NULL,
    "Word" text,
    "Meaning" text,
    "Example in French" text,
    "Example in English" text,
    "Deadline" date
);

ALTER TABLE public."Day_2" OWNER TO postgres;

CREATE TABLE public."Day_21" (
    "ID" integer NOT NULL,
    "Word" text,
    "Meaning" text,
    "Example in French" text,
    "Example in English" text,
    "Deadline" date
);

ALTER TABLE public."Day_21" OWNER TO postgres;

CREATE TABLE public."Day_4" (
    "ID" integer NOT NULL,
    "Word" text,
    "Meaning" text,
    "Example in French" text,
    "Example in English" text,
    "Deadline" date
);

ALTER TABLE public."Day_4" OWNER TO postgres;

CREATE TABLE public."Day_7" (
    "ID" integer NOT NULL,
    "Word" text,
    "Meaning" text,
    "Example in French" text,
    "Example in English" text,
    "Deadline" date
);

ALTER TABLE public."Day_7" OWNER TO postgres;

CREATE TABLE public.vocabulary (
    "ID" integer NOT NULL,
    "Word" text,
    "Meaning" text,
    "Example in French" text,
    "Example in English" text,
    "Start date" date
);

ALTER TABLE public.vocabulary OWNER TO postgres;

CREATE SEQUENCE public.vocabulary_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.vocabulary_id_seq OWNER TO postgres;

ALTER SEQUENCE public.vocabulary_id_seq OWNED BY public.vocabulary."ID";

ALTER TABLE ONLY public.vocabulary ALTER COLUMN "ID" SET DEFAULT nextval('public.vocabulary_id_seq'::regclass);

ALTER TABLE ONLY public."Day_12"
    ADD CONSTRAINT "Day_12_pkey" PRIMARY KEY ("ID");

ALTER TABLE ONLY public."Day_21"
    ADD CONSTRAINT "Day_21_pkey" PRIMARY KEY ("ID");

ALTER TABLE ONLY public."Day_2"
    ADD CONSTRAINT "Day_2_pkey" PRIMARY KEY ("ID");

ALTER TABLE ONLY public."Day_4"
    ADD CONSTRAINT "Day_4_pkey" PRIMARY KEY ("ID");

ALTER TABLE ONLY public."Day_7"
    ADD CONSTRAINT "Day_7_pkey" PRIMARY KEY ("ID");

ALTER TABLE ONLY public.vocabulary
    ADD CONSTRAINT vocabulary_pkey PRIMARY KEY ("ID");

CREATE TRIGGER auto_add_after_insert_trg AFTER INSERT ON public.vocabulary FOR EACH ROW EXECUTE FUNCTION public.auto_add_after_insert_func();

CREATE TRIGGER auto_change_date_after_update_trg AFTER UPDATE ON public.vocabulary FOR EACH ROW EXECUTE FUNCTION public.auto_change_date_after_update_func();

ALTER TABLE ONLY public."Day_2"
    ADD CONSTRAINT "FK_id" FOREIGN KEY ("ID") REFERENCES public.vocabulary("ID") ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public."Day_4"
    ADD CONSTRAINT "FK_id" FOREIGN KEY ("ID") REFERENCES public.vocabulary("ID") ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public."Day_7"
    ADD CONSTRAINT "FK_id" FOREIGN KEY ("ID") REFERENCES public.vocabulary("ID") ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public."Day_12"
    ADD CONSTRAINT "FK_id" FOREIGN KEY ("ID") REFERENCES public.vocabulary("ID") ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public."Day_21"
    ADD CONSTRAINT "FK_id" FOREIGN KEY ("ID") REFERENCES public.vocabulary("ID") ON UPDATE CASCADE ON DELETE CASCADE;

