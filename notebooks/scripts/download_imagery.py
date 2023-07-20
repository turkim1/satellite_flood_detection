from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer 
import json, os, tarfile
from shapely.geometry import Polygon
import geopandas as gpd
from scripts.credential import username_landsat, password_landsat, username_sentinel, password_sentinel
from sentinelsat.sentinel import SentinelAPI


class DownloadImagery: 

    def search_landast(self, lat, long, start_date, end_date, dataset='landsat_tm_c2_l2', max_cloud_cover=15):

        """Returns list of satellite imagery and dates from Earth Explorer.

        Arguments:
            lat {float} -- Latitude value
            long {float} -- Longitude value
            start_date {datetime} -- Start date for the API start searching Eg.: 1985-01-01
            end_date {datetime} -- End date for the API start searching Eg.: 1985-01-01
            dataset {str} -- Satellite dataset of your choice. Default is landsat_tm_c2_l2
            max_cloud_cover {int} -- Percentage of desired clouds in the scene. Default is 15%

        """


        # Initialize a new API instance and get an access key
        api = API(username_landsat, password_landsat)

        # Search for Landsat TM scenes
        scenes = api.search(
            dataset=dataset,
            latitude=lat,
            longitude=long,
            start_date=start_date,
            end_date=end_date,
            max_cloud_cover=max_cloud_cover
        )

        found_scenes = len(scenes)
        print(f"{found_scenes} scenes found.")

        # Process the result
        for scene in self.scenes:
            print(scene['acquisition_date'].strftime('%Y-%m-%d'), ' | ID:', scene['entity_id'])

            # Write scene footprints to disk
            fname = f"./geojson/{scene['landsat_product_id']}.geojson"
            with open(fname, "w") as f:
                json.dump(scene['spatial_coverage'].__geo_interface__, f)

        api.logout()
        return found_scenes

    def download_landsat(self, output_dir, id):

        """Downloads the first image from list generated in search_imagery

        Arguments:
            output_dir {str} -- Path to folder that will save the file.

        """

        ee = EarthExplorer(self.api_username, self.api_password)

        if not id:
            for scene in self.scenes:
                try:
                    ee.download(scene['entity_id'], output_dir=output_dir)
                except:
                    pass
                ee.logout()

            path = os.path.join(os.getcwd(), output_dir)
        
        else:
            ee.download(id, output_dir = output_dir)
            ee.logou()
            path = os.path.join(os.getcwd(), output_dir)

        # Removing files that are not the zipped satellite image.
        print('Removing old satellite images...')
        for root, dirs, files in os.walk(path):
            for file in files:
                if not file.endswith('.tar'):
                    os.remove(os.path.join(path, file))

        # Unzipping all satellite images from the tar folder.
        print('Unzipping images')
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.tar'):
                    landsat = os.path.join(path, file)
                    tar = tarfile.open(landsat)
                    tar.extractall(output_dir)
                    tar.close()
                    os.remove(landsat)

        #final report
        print('----------------QUICK REPORT---------------')
        print(f"{scene['entity_id']} scenes downloaded.")
        print(f"Cloud cover: {scene['scene_cloud_cover']} \nLand Cloud cover {scene['land_cloud_cover']}")
        print(f"More information in the {scene['entity_id']}_metadata.json")

    def download_sentinel(username, password, boundary, start_date, end_date, max_cloud_cover = 15):
        
        geom = boundary['geometry'].iloc[0]

        api = SentinelAPI(username,
                        password,
                        'https://scihub.copernicus.eu/dhus')
        
        products = api.query(geom,
                            date = (start_date, end_date),
                            platformname = 'Sentinel-2',
                            processinglevel = 'Level-2A',
                            cloudcoverpercentage = (0, max_cloud_cover)
                            )

        gdf = api.to_geodataframe(products)
        gdf_sorted = gdf.sort_values(by='ingestiondate')

        # filter results to show results that fully contain our desired boundary
        polya = boundary['geometry'].iloc[0]
        gdf_sorted['contains'] = gdf_sorted['geometry'].apply(lambda x:x.contains(polya))
        gdf_sorted = gdf_sorted[gdf_sorted['contains']==True]

        return gdf_sorted

    def create_square_bbox(geometry):
        #from shapely.geometry import Polygon
        # Get the bounds of the geometry column
        bounds = geometry.bounds
        
        # Extract the minimum and maximum values
        min_x = bounds["minx"].min()
        min_y = bounds["miny"].min()
        max_x = bounds["maxx"].max()
        max_y = bounds["maxy"].max()
        
        # Calculate the side length of the square
        side_length = max(max_x - min_x, max_y - min_y)
        
        # Calculate the coordinates of the square
        square_min_x = (max_x + min_x) / 2 - side_length / 2
        square_min_y = (max_y + min_y) / 2 - side_length / 2
        
        # Create a polygon representing the square bounding box
        bbox_polygon = Polygon([
            (square_min_x, square_min_y),
            (square_min_x, square_min_y + side_length),
            (square_min_x + side_length, square_min_y + side_length),
            (square_min_x + side_length, square_min_y)
        ])
        
        # Create a GeoDataFrame with the bounding box polygon
        bbox_gdf = gpd.GeoDataFrame(geometry=[bbox_polygon])
        
        return bbox_gdf

    def normalize(band):

        """Normalized raster bands

        Arguments:
            band {numpy array}
        """

        band_min, band_max = (band.min(), band.max())
        return ((band - band_min)/((band_max - band_min)))