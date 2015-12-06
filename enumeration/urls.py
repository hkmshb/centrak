from django.conf.urls import include, patterns, url


urlpatterns = patterns('enumeration.views',
    url(r'^devices/$', 'devices', name='devices'),
    url(r'^devices/create$', 'manage_device', name='device-insert'),
    url(r'^devices/update/(?P<id>[0-9]+)$', 'manage_device', name='device-update'),
    url(r'^devices/delete(/(?P<id>[0-9]+))?', 'delete_device', name='device-delete'),
    
    url(r'^device-options/manufacturers/$', 'manufacturers', name='manufacturers'),
    url(r'^device-options/manufacturers/update/(?P<id>[0-9]+)$',
        'manufacturer_update', name='manufacturer-update'),
    url(r'^device-options/manufacturers/delete(/(?P<id>[0-9]+))?', 
        'manufacturer_delete', name='manufacturer-delete'),
    
    url(r'^device-options/mobile-os/$', 'mobile_os', name='mobile-os'),
    url(r'^device-options/mobile-os/update/(?P<id>[0-9]+)$',
        'mobile_os_update', name='mobile-os-update'),
    url(r'^device-options/mobile-os/delete(/(?P<id>[0-9]+))?$',
        'mobile_os_delete', name='mobile-os-delete'),
    
    # people
    url(r'^persons/$', 'persons', name='persons'),
    url(r'^persons/create$', 'manage_person', name='person-insert'),
    url(r'^persons/delete$', 'delete_person', name='person-delete'),
    url(r'^persons/(?P<id>\d+)/',
        include([
            url(r'^update$', 'enumeration.views.manage_person', name='person-update'),
            url(r'^delete$', 'enumeration.views.delete_person', name='person-uni-delete'),
        ])
    ),
    
    # teams
    url(r'^teams/$', 'team_list', name='teams'),
    url(r'^teams/create$', 'manage_team', name='team-insert'),
    url(r'^teams/delete$', 'delete_team', name='team-delete'),
    url(r'^teams/(?P<id>\d+)/',
        include([
            url(r'^$', 'enumeration.views.view_team', name='team-view'),
            url(r'^update$', 'enumeration.views.manage_team', name='team-update'),
            url(r'^(?P<part_type>(devices|members))/$', 'enumeration.views.view_team',
                name='team-view-ext'),
            
            ## devices
            url(r'^devices/add$', 'enumeration.views.manage_team_device',
                name='team-device-add'),
            url(r'^devices/remove(/(?P<device_id>\d+))?$',
                'enumeration.views.remove_team_device',
                name='team-device-remove'),
            
            ## members
            url(r'^members/add$', 'enumeration.views.manage_team_member',
                name='team-member-add'),
            url(r'^members/remove(/(?P<member_id>\d+))?$',
                'enumeration.views.remove_team_member',
                name='team-member-remove'),
        ]),
    ),
    
    # groups
    url(r'^groups/$', 'group_list', name='groups'),
    url(r'^groups/create$', 'manage_group', name='group-insert'),
    url(r'^groups/(?P<id>\d+)/',
        include([
            url(r'^$', 'enumeration.views.view_group', name='group-view'),
            url(r'^update$', 'enumeration.views.manage_group', name='group-update'),
            
            ## teams
            url(r'^teams/add$', 'enumeration.views.manage_group_team',
                name='group-team-add'),
            url(r'^teams/remove(/(?P<team_id>\d+))?$',
                'enumeration.views.remove_group_team',
                name='group-team-remove'),
        ])
    ),
)

