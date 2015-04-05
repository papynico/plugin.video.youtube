__author__ = 'bromix'

from resources.lib import kodion
from resources.lib.kodion.items import DirectoryItem
from resources.lib.youtube.helper import v2, v3, extract_urls, UrlResolver, UrlToItemConverter
from . import utils

def _process_related_videos(provider, context, re_match):
    result = []

    provider.set_content_type(context, kodion.constants.content_type.EPISODES)

    page_token = context.get_param('page_token', '')
    video_id = context.get_param('video_id', '')
    if video_id:
        json_data = provider.get_client(context).get_related_videos(video_id=video_id, page_token=page_token)
        result.extend(v3.response_to_items(provider, context, json_data, process_next_page=False))
        pass

    return result


def _process_popular_right_now(provider, context, re_match):
    provider.set_content_type(context, kodion.constants.content_type.EPISODES)

    result = []

    page_token = context.get_param('page_token', '')
    json_data = provider.get_client(context).get_popular_videos(page_token=page_token)
    result.extend(v3.response_to_items(provider, context, json_data))

    return result


def _process_browse_channels(provider, context, re_match):
    result = []

    page_token = context.get_param('page_token', '')
    guide_id = context.get_param('guide_id', '')
    if guide_id:
        json_data = provider.get_client(context).get_guide_category(guide_id)
        result.extend(v3.response_to_items(provider, context, json_data))
        pass
    else:
        json_data = provider.get_client(context).get_guide_categories()
        result.extend(v3.response_to_items(provider, context, json_data))
        pass

    return result


def _process_new_uploaded_videos(provider, context, re_match):
    provider.set_content_type(context, kodion.constants.content_type.EPISODES)

    result = []
    start_index = int(context.get_param('start-index', 0))
    json_data = provider.get_client(context).get_uploaded_videos_of_subscriptions(start_index)
    result.extend(v2.response_to_items(provider, context, json_data))

    return result


def _process_disliked_videos(provider, context, re_match):
    result = []

    page_token = context.get_param('page_token', '')
    json_data = provider.get_client(context).get_disliked_videos(page_token=page_token)
    if not v3.handle_error(provider, context, json_data):
        return False
    result.extend(v3.response_to_items(provider, context, json_data))
    return result


def _process_live_events(provider, context, re_match):
    def _sort(x):
        return x.get_aired()

    provider.set_content_type(context, kodion.constants.content_type.EPISODES)

    result = []

    # TODO: cache result
    page_token = context.get_param('page_token', '')
    json_data = provider.get_client(context).get_live_events(event_type='live', page_token=page_token)
    if not v3.handle_error(provider, context, json_data):
        return False
    result.extend(v3.response_to_items(provider, context, json_data, sort=_sort, reverse_sort=True))

    return result


def _process_description_links(provider, context, re_match):
    def _extract(_video_id):
        provider.set_content_type(context, kodion.constants.content_type.EPISODES)

        result = []

        progress_dialog = context.get_ui().create_progress_dialog(
            heading=context.localize(kodion.constants.localize.COMMON_PLEASE_WAIT), background=False)

        resource_manager = provider.get_resource_manager(context)

        video_data = resource_manager.get_videos([_video_id])
        yt_item = video_data[_video_id]
        snippet = yt_item['snippet']  # crash if not conform
        description = kodion.utils.strip_html_from_text(snippet['description'])

        urls = extract_urls(description)

        progress_dialog.set_total(len(urls))

        url_resolver = UrlResolver()
        res_urls = []
        for url in urls:
            progress_dialog.update(steps=1, text=url)
            res_urls.append(url_resolver.resolve(url))
            pass

        url_to_item_converter = UrlToItemConverter()
        url_to_item_converter.add_urls(res_urls, provider, context)

        result.extend(url_to_item_converter.get_items(provider, context))

        progress_dialog.close()

        if len(result) == 0:
            progress_dialog.close()
            context.get_ui().on_ok(title=context.localize(provider.LOCAL_MAP['youtube.video.description.links']),
                                   text=context.localize(provider.LOCAL_MAP['youtube.video.description.links.not_found']))
            return False

        return result

    def _playlist_ids(_playlist_ids):
        _playlist_id_dict = {}
        _result = []

        for playlist_id in _playlist_ids:
            playlist_item = DirectoryItem('', context.create_uri(['playlist', playlist_id]))
            playlist_item.set_fanart(provider.get_fanart(context))
            _playlist_id_dict[playlist_id] = playlist_item
            _result.append(playlist_item)

            channel_id_dict = {}
            utils.update_playlist_infos(provider, context, _playlist_id_dict, channel_id_dict)
            utils.update_channel_infos(provider, context, channel_id_dict)

            pass
        return _result

    video_id = context.get_param('video_id', '')
    if video_id:
        return _extract(video_id)

    playlist_ids = context.get_param('playlist_ids', '')
    playlist_ids = playlist_ids.split(',')
    if len(playlist_ids) > 0:
        return _playlist_ids(playlist_ids)

    context.log_error('Missing video_id or playlist_ids for description links')

    return False


def process(category, provider, context, re_match):
    result = []

    if category == 'related_videos':
        return _process_related_videos(provider, context, re_match)
    elif category == 'popular_right_now':
        return _process_popular_right_now(provider, context, re_match)
    elif category == 'browse_channels':
        return _process_browse_channels(provider, context, re_match)
    elif category == 'new_uploaded_videos':
        return _process_new_uploaded_videos(provider, context, re_match)
    elif category == 'disliked_videos':
        return _process_disliked_videos(provider, context, re_match)
    elif category == 'live':
        return _process_live_events(provider, context, re_match)
    elif category == 'description_links':
        return _process_description_links(provider, context, re_match)
    else:
        raise kodion.KodionException("YouTube special category '%s' not found" % category)

    return result
