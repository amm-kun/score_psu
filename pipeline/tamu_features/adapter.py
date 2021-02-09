from tamu_features import PaperInfoCrawler, DataProcessor

VENUE_METADATA_FILE = r'tamu_features\venue_meta\all_venues.csv'
TRAINING_DIR = r'tamu_features\training_data'


def get_tamu_features(input_file, p_id, issn, auth):
    crawler = PaperInfoCrawler(input_file, VENUE_METADATA_FILE)
    print("Crawling Info..\n")
    # Get paper id from API in addition to meta file
    base_df, auth_df, notFoundList = crawler.simple_crawl(p_id, issn, auth)
    # base_df, auth_df, downstream_df, notFoundList = crawler.crawl('gw38')
    print("\nCrawling Finished. Processing data..\n")
    google_scholar_data = False
    if len(notFoundList) > 0:
        google_scholar_data = True
    data_processor = DataProcessor(TRAINING_DIR, google_scholar_data)
    # No downstream for now
    # processed_df, imputed_list = data_processor.processData(base_df, auth_df, downstream_df)
    processed_df, imputed_list = data_processor.processData(base_df, auth_df)
    return processed_df.to_dict('records')[0], imputed_list
