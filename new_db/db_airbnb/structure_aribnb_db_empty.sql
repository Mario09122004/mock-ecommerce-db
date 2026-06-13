--
-- PostgreSQL database dump
--

\restrict 6MICo38pGa8S7YPbif0hnWAdOCiE1FMPg70jXkQLElMMdzyPi3vMyuc767QeBWS

-- Dumped from database version 14.22 (Debian 14.22-1.pgdg12+1)
-- Dumped by pg_dump version 18.4

-- Started on 2026-06-11 18:22:53 CST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 5 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: admin
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 209 (class 1259 OID 24962)
-- Name: cat_neighbourhoods; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.cat_neighbourhoods (
    id integer NOT NULL,
    neighbourhood_group text,
    neighbourhood text
);


ALTER TABLE public.cat_neighbourhoods OWNER TO admin;

--
-- TOC entry 210 (class 1259 OID 24967)
-- Name: cat_neighbourhoods_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.cat_neighbourhoods_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cat_neighbourhoods_id_seq OWNER TO admin;

--
-- TOC entry 3412 (class 0 OID 0)
-- Dependencies: 210
-- Name: cat_neighbourhoods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.cat_neighbourhoods_id_seq OWNED BY public.cat_neighbourhoods.id;


--
-- TOC entry 211 (class 1259 OID 24968)
-- Name: cat_property_types; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.cat_property_types (
    id integer NOT NULL,
    property_type text
);


ALTER TABLE public.cat_property_types OWNER TO admin;

--
-- TOC entry 212 (class 1259 OID 24973)
-- Name: cat_room_types; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.cat_room_types (
    id integer NOT NULL,
    room_type text
);


ALTER TABLE public.cat_room_types OWNER TO admin;

--
-- TOC entry 213 (class 1259 OID 24978)
-- Name: data_hosts; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.data_hosts (
    id bigint NOT NULL,
    host_name text,
    host_url text,
    host_location text,
    host_about text,
    host_is_superhost boolean
);


ALTER TABLE public.data_hosts OWNER TO admin;

--
-- TOC entry 214 (class 1259 OID 24983)
-- Name: data_listings; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.data_listings (
    id bigint NOT NULL,
    name text,
    description text,
    host_id bigint,
    neighbourhood_id integer,
    property_type_id integer,
    room_type_id integer,
    latitude numeric,
    longitude numeric,
    accommodates integer,
    bathrooms numeric,
    bedrooms integer,
    beds integer,
    price numeric,
    minimum_nights integer,
    maximum_nights integer,
    CONSTRAINT chk_accommodates CHECK ((accommodates > 0)),
    CONSTRAINT chk_latitude CHECK (((latitude >= ('-90'::integer)::numeric) AND (latitude <= (90)::numeric))),
    CONSTRAINT chk_listings_price CHECK ((price >= (0)::numeric)),
    CONSTRAINT chk_longitude CHECK (((longitude >= ('-180'::integer)::numeric) AND (longitude <= (180)::numeric))),
    CONSTRAINT chk_min_nights CHECK ((minimum_nights > 0))
);


ALTER TABLE public.data_listings OWNER TO admin;

--
-- TOC entry 215 (class 1259 OID 24993)
-- Name: data_reviewers; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.data_reviewers (
    id bigint NOT NULL,
    reviewer_name text
);


ALTER TABLE public.data_reviewers OWNER TO admin;

--
-- TOC entry 216 (class 1259 OID 24998)
-- Name: hist_calendar; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.hist_calendar (
    id integer NOT NULL,
    listing_id bigint,
    date date,
    available boolean,
    price numeric,
    minimum_nights integer,
    maximum_nights integer,
    CONSTRAINT chk_calendar_price CHECK ((price >= (0)::numeric))
);


ALTER TABLE public.hist_calendar OWNER TO admin;

--
-- TOC entry 217 (class 1259 OID 25004)
-- Name: hist_calendar_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.hist_calendar_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hist_calendar_id_seq OWNER TO admin;

--
-- TOC entry 3413 (class 0 OID 0)
-- Dependencies: 217
-- Name: hist_calendar_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.hist_calendar_id_seq OWNED BY public.hist_calendar.id;


--
-- TOC entry 218 (class 1259 OID 25005)
-- Name: hist_reviews; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.hist_reviews (
    id bigint NOT NULL,
    listing_id bigint NOT NULL,
    reviewer_id bigint NOT NULL,
    date date NOT NULL,
    comments text
);


ALTER TABLE public.hist_reviews OWNER TO admin;

--
-- TOC entry 3219 (class 2604 OID 25010)
-- Name: cat_neighbourhoods id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.cat_neighbourhoods ALTER COLUMN id SET DEFAULT nextval('public.cat_neighbourhoods_id_seq'::regclass);


--
-- TOC entry 3220 (class 2604 OID 25011)
-- Name: hist_calendar id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.hist_calendar ALTER COLUMN id SET DEFAULT nextval('public.hist_calendar_id_seq'::regclass);


--
-- TOC entry 3396 (class 0 OID 24962)
-- Dependencies: 209
-- Data for Name: cat_neighbourhoods; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.cat_neighbourhoods (id, neighbourhood_group, neighbourhood) FROM stdin;
\.


--
-- TOC entry 3398 (class 0 OID 24968)
-- Dependencies: 211
-- Data for Name: cat_property_types; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.cat_property_types (id, property_type) FROM stdin;
\.


--
-- TOC entry 3399 (class 0 OID 24973)
-- Dependencies: 212
-- Data for Name: cat_room_types; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.cat_room_types (id, room_type) FROM stdin;
\.


--
-- TOC entry 3400 (class 0 OID 24978)
-- Dependencies: 213
-- Data for Name: data_hosts; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.data_hosts (id, host_name, host_url, host_location, host_about, host_is_superhost) FROM stdin;
\.


--
-- TOC entry 3401 (class 0 OID 24983)
-- Dependencies: 214
-- Data for Name: data_listings; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.data_listings (id, name, description, host_id, neighbourhood_id, property_type_id, room_type_id, latitude, longitude, accommodates, bathrooms, bedrooms, beds, price, minimum_nights, maximum_nights) FROM stdin;
\.


--
-- TOC entry 3402 (class 0 OID 24993)
-- Dependencies: 215
-- Data for Name: data_reviewers; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.data_reviewers (id, reviewer_name) FROM stdin;
\.


--
-- TOC entry 3403 (class 0 OID 24998)
-- Dependencies: 216
-- Data for Name: hist_calendar; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.hist_calendar (id, listing_id, date, available, price, minimum_nights, maximum_nights) FROM stdin;
\.


--
-- TOC entry 3405 (class 0 OID 25005)
-- Dependencies: 218
-- Data for Name: hist_reviews; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.hist_reviews (id, listing_id, reviewer_id, date, comments) FROM stdin;
\.


--
-- TOC entry 3414 (class 0 OID 0)
-- Dependencies: 210
-- Name: cat_neighbourhoods_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.cat_neighbourhoods_id_seq', 16, true);


--
-- TOC entry 3415 (class 0 OID 0)
-- Dependencies: 217
-- Name: hist_calendar_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.hist_calendar_id_seq', 165345, true);


--
-- TOC entry 3228 (class 2606 OID 25023)
-- Name: cat_neighbourhoods cat_neighbourhoods_neighbourhood_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.cat_neighbourhoods
    ADD CONSTRAINT cat_neighbourhoods_neighbourhood_key UNIQUE (neighbourhood);


--
-- TOC entry 3230 (class 2606 OID 25025)
-- Name: cat_neighbourhoods cat_neighbourhoods_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.cat_neighbourhoods
    ADD CONSTRAINT cat_neighbourhoods_pkey PRIMARY KEY (id);


--
-- TOC entry 3232 (class 2606 OID 25027)
-- Name: cat_property_types cat_property_types_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.cat_property_types
    ADD CONSTRAINT cat_property_types_pkey PRIMARY KEY (id);


--
-- TOC entry 3234 (class 2606 OID 25029)
-- Name: cat_property_types cat_property_types_property_type_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.cat_property_types
    ADD CONSTRAINT cat_property_types_property_type_key UNIQUE (property_type);


--
-- TOC entry 3236 (class 2606 OID 25031)
-- Name: cat_room_types cat_room_types_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.cat_room_types
    ADD CONSTRAINT cat_room_types_pkey PRIMARY KEY (id);


--
-- TOC entry 3238 (class 2606 OID 25033)
-- Name: cat_room_types cat_room_types_room_type_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.cat_room_types
    ADD CONSTRAINT cat_room_types_room_type_key UNIQUE (room_type);


--
-- TOC entry 3240 (class 2606 OID 25035)
-- Name: data_hosts data_hosts_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.data_hosts
    ADD CONSTRAINT data_hosts_pkey PRIMARY KEY (id);


--
-- TOC entry 3242 (class 2606 OID 25037)
-- Name: data_listings data_listings_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.data_listings
    ADD CONSTRAINT data_listings_pkey PRIMARY KEY (id);


--
-- TOC entry 3244 (class 2606 OID 25039)
-- Name: data_reviewers data_reviewers_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.data_reviewers
    ADD CONSTRAINT data_reviewers_pkey PRIMARY KEY (id);


--
-- TOC entry 3246 (class 2606 OID 25041)
-- Name: hist_calendar hist_calendar_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.hist_calendar
    ADD CONSTRAINT hist_calendar_pkey PRIMARY KEY (id);


--
-- TOC entry 3249 (class 2606 OID 25043)
-- Name: hist_reviews hist_reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.hist_reviews
    ADD CONSTRAINT hist_reviews_pkey PRIMARY KEY (id);


--
-- TOC entry 3247 (class 1259 OID 25044)
-- Name: idx_hist_calendar_listing_date; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_hist_calendar_listing_date ON public.hist_calendar USING btree (listing_id, date);


--
-- TOC entry 3250 (class 2606 OID 25045)
-- Name: data_listings fk_host; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.data_listings
    ADD CONSTRAINT fk_host FOREIGN KEY (host_id) REFERENCES public.data_hosts(id);


--
-- TOC entry 3254 (class 2606 OID 25050)
-- Name: hist_calendar fk_listing_cal; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.hist_calendar
    ADD CONSTRAINT fk_listing_cal FOREIGN KEY (listing_id) REFERENCES public.data_listings(id);


--
-- TOC entry 3255 (class 2606 OID 25055)
-- Name: hist_reviews fk_listing_rev; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.hist_reviews
    ADD CONSTRAINT fk_listing_rev FOREIGN KEY (listing_id) REFERENCES public.data_listings(id);


--
-- TOC entry 3251 (class 2606 OID 25060)
-- Name: data_listings fk_neighbourhood; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.data_listings
    ADD CONSTRAINT fk_neighbourhood FOREIGN KEY (neighbourhood_id) REFERENCES public.cat_neighbourhoods(id);


--
-- TOC entry 3252 (class 2606 OID 25065)
-- Name: data_listings fk_property_type; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.data_listings
    ADD CONSTRAINT fk_property_type FOREIGN KEY (property_type_id) REFERENCES public.cat_property_types(id);


--
-- TOC entry 3256 (class 2606 OID 25070)
-- Name: hist_reviews fk_reviewer_rev; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.hist_reviews
    ADD CONSTRAINT fk_reviewer_rev FOREIGN KEY (reviewer_id) REFERENCES public.data_reviewers(id) ON DELETE CASCADE;


--
-- TOC entry 3253 (class 2606 OID 25075)
-- Name: data_listings fk_room_type; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.data_listings
    ADD CONSTRAINT fk_room_type FOREIGN KEY (room_type_id) REFERENCES public.cat_room_types(id) ON DELETE CASCADE;


--
-- TOC entry 3411 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: admin
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2026-06-11 18:22:53 CST

--
-- PostgreSQL database dump complete
--

\unrestrict 6MICo38pGa8S7YPbif0hnWAdOCiE1FMPg70jXkQLElMMdzyPi3vMyuc767QeBWS

