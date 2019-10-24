CREATE TABLE "UserInfo" (
  "id" SERIAL PRIMARY KEY,
  "full_name" varchar,
  "created_at" timestamp,
  "phone_number" varchar
);

CREATE TABLE "Client" (
  "id" int SERIAL PRIMARY KEY,
  "user_info" int
);

CREATE TABLE "Dispatch" (
  "id" int SERIAL PRIMARY KEY,
  "user_info" int
);

CREATE TABLE "Car" (
  "id" int SERIAL PRIMARY KEY,
  "photos" file,
  "number" int,
  "name" varchar,
  "owner" int
);

CREATE TABLE "Driver" (
  "id" int SERIAL PRIMARY KEY,
  "license" file,
  "user_info" int
);

CREATE TABLE "Route" (
  "id" int SERIAL PRIMARY KEY,
  "driver" int,
  "price" int,
  "dest_city" int,
  "source_vity" int,
  "free_spaces" int,
  "time" datetime
);

CREATE TABLE "PickUpPlace" (
  "id" int SERIAL PRIMARY KEY,
  "place" varchar
);

CREATE TABLE "Trip" (
  "id" int SERIAL PRIMARY KEY,
  "user" int,
  "status" varchar,
  "spaces" int,
  "route" int,
  "pick_up_time" datetime,
  "pick_up_place" int
);

CREATE TABLE "FavouriteTrip" (
  "id" int SERIAL PRIMARY KEY,
  "trip" int,
  "user" int
);

CREATE TABLE "City" (
  "id" int SERIAL PRIMARY KEY,
  "name" varchar
);

ALTER TABLE "Client" ADD FOREIGN KEY ("user_info") REFERENCES "UserInfo" ("id");

ALTER TABLE "Dispatch" ADD FOREIGN KEY ("user_info") REFERENCES "UserInfo" ("id");

ALTER TABLE "Car" ADD FOREIGN KEY ("owner") REFERENCES "Driver" ("id");

ALTER TABLE "Driver" ADD FOREIGN KEY ("user_info") REFERENCES "UserInfo" ("id");

ALTER TABLE "Route" ADD FOREIGN KEY ("driver") REFERENCES "Driver" ("id");

ALTER TABLE "Route" ADD FOREIGN KEY ("dest_city") REFERENCES "City" ("id");

ALTER TABLE "Route" ADD FOREIGN KEY ("source_vity") REFERENCES "City" ("id");

ALTER TABLE "Trip" ADD FOREIGN KEY ("user") REFERENCES "Client" ("id");

ALTER TABLE "Trip" ADD FOREIGN KEY ("route") REFERENCES "Route" ("id");

ALTER TABLE "Trip" ADD FOREIGN KEY ("pick_up_place") REFERENCES "PickUpPlace" ("id");

ALTER TABLE "FavouriteTrip" ADD FOREIGN KEY ("trip") REFERENCES "Trip" ("id");

ALTER TABLE "FavouriteTrip" ADD FOREIGN KEY ("user") REFERENCES "Client" ("id");
