from resources.lib import kodion

__author__ = 'bromix'


def _process_play_video(provider, context, re_match):
    """
    plugin://plugin.video.youtube/?action=play_video&videoid=[ID]
    """
    video_id = context.get_param('videoid', '')
    if not video_id:
        raise kodion.KodimonException('old_actions/play_video: missing video_id')

    context.log_warning('DEPRECATED "%s"' % context.get_uri())
    context.log_warning('USE INSTEAD "plugin://%s/play/?video_id=%s"' % (context.get_id(), video_id))
    new_params = {'video_id': video_id}
    new_path = '/play/'
    new_context = context.clone(new_path=new_path, new_params=new_params)
    return provider.on_play(new_context, re_match)


def _process_play_all(provider, context, re_match):
    """
    plugin://plugin.video.youtube/?path=/root/video&action=play_all&playlist=PL8_6CHho8Tq4Iie-oNxb-g0ECxIhq3CxW
    """
    playlist_id = context.get_param('playlist', '')
    if not playlist_id:
        raise kodion.KodimonException('old_actions/play_all: missing playlist_id')

    context.log_warning('DEPRECATED "%s"' % context.get_uri())
    context.log_warning('USE INSTEAD "plugin://%s/play/?playlist_id=%s"' % (context.get_id(), playlist_id))
    new_params = {'playlist_id': playlist_id}
    new_path = '/play/'
    new_context = context.clone(new_path=new_path, new_params=new_params)
    return provider.on_play(new_context, re_match)


def process_old_action(provider, context, re_match):
    action = context.get_param('action', '')
    if action == 'play_video':
        return _process_play_video(provider, context, re_match)
    elif action == 'play_all':
        return _process_play_all(provider, context, re_match)
    else:
        raise kodion.KodimonException('old_actions: unknown action "%s"' % action)
    pass
