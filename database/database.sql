---- buildings

ALTER TABLE buildings DROP COLUMN fclass;
UPDATE buildings SET type = 'building' WHERE type IS NULL OR type = '';
UPDATE buildings SET type = REPLACE(type, '_', ' ') WHERE type LIKE '%_%';

---- osm_buildings

ALTER TABLE osm_buildings RENAME COLUMN geometry TO geom;
ALTER TABLE osm_buildings RENAME COLUMN "addr:city" TO city;
ALTER TABLE osm_buildings RENAME COLUMN "addr:country" TO country;
ALTER TABLE osm_buildings DROP COLUMN "addr:full";
ALTER TABLE osm_buildings RENAME COLUMN "addr:housenumber" TO housenumber;
ALTER TABLE osm_buildings RENAME COLUMN "addr:housename" TO housename;
ALTER TABLE osm_buildings RENAME COLUMN "addr:postcode" TO postcode;
UPDATE osm_buildings SET "addr:street" = "addr:place" WHERE "addr:street" IS NULL OR "addr:street" = '';
ALTER TABLE osm_buildings DROP COLUMN "addr:place";
ALTER TABLE osm_buildings RENAME COLUMN "addr:street" TO street;
ALTER TABLE osm_buildings DROP COLUMN "operator";
ALTER TABLE osm_buildings DROP COLUMN "ref";
ALTER TABLE osm_buildings DROP COLUMN "url";
ALTER TABLE osm_buildings DROP COLUMN "visible";
UPDATE osm_buildings SET building = 'building' WHERE building = 'yes';
UPDATE osm_buildings SET building = amenity WHERE not (amenity IS NULL or amenity = '');
ALTER TABLE osm_buildings DROP COLUMN amenity;
ALTER TABLE osm_buildings RENAME COLUMN building TO type;
ALTER TABLE osm_buildings RENAME COLUMN "building:flats" TO flats;
ALTER TABLE osm_buildings DROP COLUMN levels;
ALTER TABLE osm_buildings RENAME COLUMN "building:levels" TO levels;
ALTER TABLE osm_buildings DROP COLUMN "building:material";
ALTER TABLE osm_buildings RENAME COLUMN "building:max_level" TO max_level;
ALTER TABLE osm_buildings RENAME COLUMN "building:min_level" TO min_level;
ALTER TABLE osm_buildings DROP COLUMN "building:use";
ALTER TABLE osm_buildings DROP COLUMN craft;
ALTER TABLE osm_buildings DROP COLUMN landuse,DROP COLUMN office,DROP COLUMN shop;
ALTER TABLE osm_buildings DROP COLUMN source,DROP COLUMN start_date,DROP COLUMN timestamp;
ALTER TABLE osm_buildings DROP COLUMN version,DROP COLUMN tags,DROP COLUMN osm_type;
ALTER TABLE osm_buildings DROP COLUMN changeset;

DELETE FROM osm_buildings WHERE geometrytype(geom) = 'MULTILINESTRING' or geometrytype(geom) = 'LINESTRING';

DELETE FROM osm_buildings
WHERE NOT ST_Within(osm_buildings.geom, (SELECT geom FROM osm_boundaries WHERE name = 'Greater London'));

---- osm_boundaries
ALTER TABLE osm_boundaries RENAME COLUMN geometry TO geom;
DELETE FROM osm_boundaries where admin_level<>'5' and admin_level<>'6' and admin_level<>'8';
