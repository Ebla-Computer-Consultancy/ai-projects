import json
from wrapperfunction.core import config
import wrapperfunction.search.integration.aisearch_connector as aisearchconnector
from wrapperfunction.search.model.search_criterial import searchCriteria

def search(bot_name: str,rs: searchCriteria):
    try:
        # Get the search terms from the request form
        search_text = rs.query
        # If a facet is selected, use it in a filter
        filter_expression = None
        if rs.facet:
            filter_expression = "metadata_author eq '{0}'".format(rs.facet)
        sort_expression = "search.score()"
        chatbot_settings = config.load_chatbot_settings(bot_name)
        # submit the query and get the results
        results = aisearchconnector.search_query(
            chatbot_settings.index_name,
            search_text,
            filter_expression,
            sort_expression,
            rs.page_size,
            rs.page_number,
        )
        # render the results
        return results

    except Exception as error:
        return json.dumps({"error": True, "message": str(error)})
