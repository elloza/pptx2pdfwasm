/* -*- Mode: JS; tab-width: 2; indent-tabs-mode: nil; js-indent-level: 2; fill-column: 100 -*- */
// SPDX-License-Identifier: MIT

// Debugging note:
// Switch the web worker in the browsers debug tab to debug this code.
// It's the "em-pthread" web worker with the most memory usage, where "zetajs" is defined.

'use strict';

// global variables - zetajs environment:
let zetajs, css;

// = global variables (some are global for easier debugging) =
// common variables:
let context, desktop, xModel;
// example specific:
let bean_hidden, bean_overwrite, bean_pdf_export, from, to;

function demo() {
  context = zetajs.getUnoComponentContext();
  desktop = css.frame.Desktop.create(context);

  bean_hidden = new css.beans.PropertyValue({
    Name: 'Hidden',
    Value: true
  });
  bean_overwrite = new css.beans.PropertyValue({
    Name: 'Overwrite',
    Value: true
  });
  bean_pdf_export = new css.beans.PropertyValue({
    Name: 'FilterName',
    Value: 'writer_pdf_Export'
  });

  zetajs.mainPort.onmessage = function(e) {
    switch (e.data.cmd) {
      case 'convert':
        try {
          // Close old document in advance. Keep document open afterwards for debugging.
          if (xModel !== undefined &&
            xModel.queryInterface(zetajs.type.interface(css.util.XCloseable))) {
            xModel.close(false);
          }
          from = e.data.from;
          to = e.data.to;
          xModel = desktop.loadComponentFromURL('file://' + from, '_blank', 0, [bean_hidden]);
          xModel.storeToURL('file://' + to, [bean_overwrite, bean_pdf_export]);
          zetajs.mainPort.postMessage({
            cmd: 'converted',
            name: e.data.name,
            from,
            to
          });
        } catch (e) {
          const exc = zetajs.catchUnoException(e);
          console.log('TODO', zetajs.getAnyType(exc), exc.Message);
        }
        break;
      default:
        throw Error('Unknonwn message command ' + e.data.cmd);
    }
  }

  zetajs.mainPort.postMessage({
    cmd: 'start'
  });
}

Module.zetajs.then(function(pZetajs) {
  // initializing zetajs environment:
  zetajs = pZetajs;
  css = zetajs.uno.com.sun.star;
  demo(); // launching demo
});

/* vim:set shiftwidth=2 softtabstop=2 expandtab cinoptions=b1,g0,N-s cinkeys+=0=break: */