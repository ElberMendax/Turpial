# -*- coding: utf-8 -*-

# Widget para mostrar estados en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Jun 25, 2009

import gtk
import pango
import gobject
import logging

from turpial.ui import util as util
from turpial.ui.gtk.menu import Menu

log = logging.getLogger('Gtk:Statuslist')

FIELDS = 16

class StatusList(gtk.ScrolledWindow):
    def __init__(self, mainwin, mark_new=False):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_IN)
        
        self.last = None    # Last tweets updated
        self.mainwin = mainwin
        self.mark_new = mark_new
        #self.autoscroll = True
        self.popup_menu = Menu(mainwin)
        
        self.list = gtk.TreeView()
        self.list.set_headers_visible(False)
        self.list.set_events(gtk.gdk.POINTER_MOTION_MASK)
        self.list.set_level_indentation(0)
        #self.list.set_rules_hint(True)
        self.list.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        
        self.model = gtk.ListStore(
            gtk.gdk.Pixbuf, # avatar
            str, # username
            str, # datetime
            str, # client
            str, # pango_message
            str, # real_message
            str, # id
            bool, # favorited?
            gobject.TYPE_PYOBJECT, # in_reply_to_id
            gobject.TYPE_PYOBJECT, # in_reply_to_user
            gobject.TYPE_PYOBJECT, # retweeted_by
            gtk.gdk.Color, # color
            str, # update type
            str, # protocol
            bool, # own status?
            bool, # new status?
            str, #timestamp original
        ) # Editar FIELDS
        
        self.list.set_model(self.model)
        cell_avatar = gtk.CellRendererPixbuf()
        cell_avatar.set_property('yalign', 0)
        self.cell_tweet = gtk.CellRendererText()
        self.cell_tweet.set_property('wrap-mode', pango.WRAP_WORD)
        self.cell_tweet.set_property('wrap-width', 260)
        self.cell_tweet.set_property('yalign', 0)
        self.cell_tweet.set_property('xalign', 0)
        
        column = gtk.TreeViewColumn('tweets')
        column.set_alignment(0.0)
        column.pack_start(cell_avatar, False)
        column.pack_start(self.cell_tweet, True)
        column.set_attributes(self.cell_tweet, markup=4, cell_background_gdk=11)
        column.set_attributes(cell_avatar, pixbuf=0, cell_background_gdk=11)
        self.list.append_column(column)
        self.list.connect("button-release-event", self.__on_click)
            
        self.add(self.list)
        self.cursor = Cursor(self.list, self.model)
        
    def __highlight_hashtags(self, text):
        hashtags = util.detect_hashtags(text)
        if len(hashtags) == 0: return text
        
        for h in hashtags:
            torep = '%s' % h
            try:
                cad = '<span foreground="%s">%s</span>' % \
                    (self.mainwin.link_color, h)
                text = text.replace(torep, cad)
            except:
                log.debug('Problemas para resaltar el hashtag: %s' % h)
        return text
        
    def __highlight_groups(self, text):
        if not self.mainwin.request_groups_url(): 
            return text
        
        groups = util.detect_groups(text)
        if len(groups) == 0: return text
        
        for h in groups:
            torep = '%s' % h
            try:
                cad = '<span foreground="%s">%s</span>' % \
                    (self.mainwin.link_color, h)
                text = text.replace(torep, cad)
            except:
                log.debug('Problemas para resaltar el grupo: %s' % h)
        return text
        
    def __highlight_mentions(self, text):
        mentions = util.detect_mentions(text)
        if len(mentions) == 0:
            return text
        
        for h in mentions:
            if len(h) == 1: 
                continue
            torep = '%s' % h
            cad = '<span foreground="%s">%s</span>' % \
                  (self.mainwin.link_color, h)
            text = text.replace(torep, cad)
        return text
        
    def __highlight_urls(self, urls, text):
        #if len(urls) == 0: return text
        
        for u in urls:
            cad = '<span foreground="%s">%s</span>' % \
                  (self.mainwin.link_color, u)
            text = text.replace(u, cad)
        return text
        
    def __on_click(self, widget, event):
        model, row = widget.get_selection().get_selected()
        if (row is None):
            return False
        
        if model.get_value(row, 15):
            path = model.get_path(row)
            self.__mark_as_read(model, path, row)
        
        if (event.button == 3):
            self.__popup_menu(model, row, event)
        
    def __popup_menu(self, model, row, event):
        user = model.get_value(row, 1)
        msg = model.get_value(row, 5)
        uid = model.get_value(row, 6)
        in_reply_to_id = model.get_value(row, 8)
        utype = model.get_value(row, 12)
        protocol = model.get_value(row, 13)
        own = model.get_value(row, 14)
            
        menu = self.popup_menu.build(uid, user, msg, in_reply_to_id, utype, 
            protocol, own)
        menu.show_all()
        menu.popup(None, None, None, event.button , event.time)
    
    def __get_background_color(self, fav, own, msg, new):
        ''' Returns the bg color for an update according it status '''
        #naranja = gtk.gdk.Color(250 * 257, 241 * 257, 205 * 257)
        #amarillo = gtk.gdk.Color(255 * 257, 251 * 257, 230 * 257)
        #verde = gtk.gdk.Color(233 * 257, 247 * 257, 233 * 257)
        #azul = gtk.gdk.Color(235 * 257, 242 * 257, 255 * 257)
        
        azul = gtk.gdk.Color(229 * 257, 236 * 257, 255 * 257)
        rojo = gtk.gdk.Color(255 * 257, 229 * 257, 229 * 257)
        morado = gtk.gdk.Color(238 * 257, 229 * 257, 255 * 257)
        cyan = gtk.gdk.Color(229 * 257, 255 * 257, 253 * 257)
        verde = gtk.gdk.Color(229 * 257, 255 * 257, 230 * 257)
        amarillo = gtk.gdk.Color(253 * 257, 255 * 257, 229 * 257)
        naranja = gtk.gdk.Color(255 * 257, 240 * 257, 229 * 257)
        
        me = '@'+self.mainwin.me.lower()
        mention = True if msg.lower().find(me) >= 0 else False
        
        if new:
            color = azul
        elif fav:
            color = naranja
        elif own:
            color = rojo
        elif mention:
            color = verde
        else:
            color = None
            
        return color

#~ ****************************************************************************************
#~ ***************                                                          ***************
#~ *************** ESTADO NEW DEBE PERDURAR A TRAVÉS DE LAS ACTUALIZACIONES ***************
#~ ***************                                                          ***************
#~ ****************************************************************************************

    def __build_pango_text(self, status):
        ''' Transform the regular text into pango markup '''
        urls = [gobject.markup_escape_text(u) \
                for u in util.detect_urls(status.text)]
        
        pango_twt = util.unescape_text(status.text)
        pango_twt = gobject.markup_escape_text(pango_twt)
        
        user = '<span size="9000" foreground="%s"><b>%s</b></span> ' % \
            (self.mainwin.link_color, status.username)
        pango_twt = '<span size="9000">%s</span>' % pango_twt
        pango_twt = self.__highlight_hashtags(pango_twt)
        pango_twt = self.__highlight_groups(pango_twt)
        pango_twt = self.__highlight_mentions(pango_twt)
        pango_twt = self.__highlight_urls(urls, pango_twt)
        pango_twt += '<span size="2000">\n\n</span>'
        
        try:
            pango_twt = user + pango_twt
        except UnicodeDecodeError:
            clear_txt = ''
            invalid_chars = []
            for c in pango_twt:
                try:
                    clear_txt += c.encode('ascii')
                except UnicodeDecodeError:
                    invalid_chars.append(c)
                    clear_txt += '?'
            log.debug('Problema con caracteres inválidos en un tweet: %s' % invalid_chars)
            pango_twt = clear_txt
        
        footer = '<span size="small" foreground="#999">%s' % status.datetime
        if status.source: 
            footer += ' %s %s' % (_('from'), status.source)
        if status.in_reply_to_user:
            footer += ' %s %s' % (_('in reply to'), status.in_reply_to_user)
        if status.retweet_by:
            footer += '\n%s %s' % (_('Retweeted by'), status.retweet_by)
        footer += '</span>'
        pango_twt += footer
        
        return pango_twt
        
    def __update_pic(self, model, path, iter, args):
        user, pic = args
        username = model.get_value(iter, 1)
        if username == user:
            model.set_value(iter, 0, pic)
            return True
        return False
        
    def __build_iter_status(self, status, new=False):
        p = self.mainwin.parse_tweet(status)
        
        pix = self.mainwin.get_user_avatar(p.username, p.avatar)
        pango_text = self.__build_pango_text(p)
        color = self.__get_background_color(p.is_favorite, p.is_own, p.text, new)
        
        row = [pix, p.username, p.datetime, p.source, pango_text, p.text, p.id, 
            p.is_favorite, p.in_reply_to_id, p.in_reply_to_user, p.retweet_by, 
            color, p.type, p.protocol, p.is_own, new, p.timestamp]
        
        del pix
        return row
        
    def __add_status(self, model, path, iter, statuses):
        ''' Append status '''
        index = path[0]
        stored_id = model.get_value(iter, 6)
        if statuses[index].id != stored_id:
            row = self.__build_iter_status(statuses[index], new=True)
            for i in range(FIELDS + 1):
                model.set_value(iter, i, row[i])
        return False
    
    def __add_statuses(self, statuses):
        ''' Append statuses to list'''
        for status in statuses:
            row = self.__build_iter_status(status)
            self.model.append(row)
    
    def __modify_statuses(self, statuses):
        index = 0
        to_del = []
        prev_new = []
        new_count = 0
        iter = self.model.get_iter_first()
        
        while iter:
            stored_id = self.model.get_value(iter, 6)
            try:
                if statuses[index].id != stored_id:
                    # Setting as new
                    if self.model.get_value(iter, 15):
                        prev_new.append(stored_id)
                    new = False
                    if self.__is_new(statuses[index]):
                        new_count += 1
                        new = True
                    if statuses[index].id in prev_new:
                        new = True
                    row = self.__build_iter_status(statuses[index], new=new)
                    
                    for i in range(FIELDS + 1):
                        self.model.set_value(iter, i, row[i])
            except IndexError:
                to_del.append(iter)
            iter = self.model.iter_next(iter)
            index += 1
        
        if len(statuses) > index:
            self.__add_statuses(statuses[index + 1:])
        elif len(statuses) < index:
            for iter in to_del:
                self.model.remove(iter)
        
        return new_count
        
    def __update_cursor(self, model, path, iter):
        if self.cursor.path == (0, ):
            return True
        
        stored_id = model.get_value(iter, 6)
        if stored_id == self.cursor.cid:
            self.cursor.update(iter)
            return True
        return False
        
    def __set_last_time(self):
        self.last_time = None
        if not self.last:
            return
        
        for status in self.last:
            if status.username != self.mainwin.me:
                self.last_time = status.timestamp
                break
        
    def __is_new(self, status):
        if status.username != self.mainwin.me:
            if status.timestamp > self.last_time:
                return True
        return False
        
    def __mark_as_read(self, model, path, iter):
        msg = self.model.get_value(iter, 5)
        fav = self.model.get_value(iter, 7)
        own = self.model.get_value(iter, 14)
        color = self.__get_background_color(fav, own, msg, False)
        self.model.set_value(iter, 11, color)
        
    def clear(self):
        self.model.clear()
        
    def update_wrap(self, val):
        self.cell_tweet.set_property('wrap-width', val - 85)
        iter = self.model.get_iter_first()
        while iter:
            path = self.model.get_path(iter)
            self.model.row_changed(path, iter)
            iter = self.model.iter_next(iter)
    
    def update(self, statuses):
        self.cursor.mark()
        self.__set_last_time()
        
        new_count = 0
        if len(self.model) == 0:
            self.__add_statuses(statuses)
        else:
            new_count = self.__modify_statuses(statuses)
        
        self.model.foreach(self.__update_cursor)
        self.last = statuses
        return new_count
    
    def update_user_pic(self, user, pic):
        pix = self.mainwin.load_avatar(self.mainwin.imgdir, pic)
        self.model.foreach(self.__update_pic, (user, pix))
        del pix
        
    def mark_all_as_read(self):
        self.model.foreach(self.__mark_as_read)

class Cursor:
    def __init__(self, list, model):
        self.__list = list
        self.__model = model
        self.path = None
        self.cid = None
        
    def mark(self):
        self.path, col = self.__list.get_cursor()
        if self.path:
            iter = self.__model.get_iter(self.path)
            self.cid = self.__model.get_value(iter, 6)
        
    def update(self, iter):
        self.path = self.__model.get_path(iter)
        self.__list.set_cursor(self.path)
        
