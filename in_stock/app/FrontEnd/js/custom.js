
  (function ($) {
  
  "use strict";

    // NAVBAR
    $('.navbar-collapse a').on('click',function(){
      $(".navbar-collapse").collapse('hide');
    });

    $(function() {
      $('.hero-slides').vegas({
          slides: [
              { src: 'images/slides/trabalhador-de-armazem-com-capacete-de-seguranca-conversando-ao-telefone-e-segurando-uma-lista-de-verificacao-na-instalacao-armazem-de-distribuicao.jpg' },
              { src: 'images/slides/dispositivo-de-sustentacao-de-homem-de-tiro-medio.jpg' },
              { src: 'images/slides/trabalhadora-negra-armazem-passando-pela-lista-de-remessas-enquanto-verifica-o-estoque-no-compartimento-de-armazenamento-industrial.jpg' }
          ],
          timer: false,
          animation: 'kenburns',
      });
    });
    
    // CUSTOM LINK
    $('.smoothscroll').click(function(){
      var el = $(this).attr('href');
      var elWrapped = $(el);
      var header_height = $('.navbar').height() + 60;
  
      scrollToDiv(elWrapped,header_height);
      return false;
  
      function scrollToDiv(element,navheight){
        var offset = element.offset();
        var offsetTop = offset.top;
        var totalScroll = offsetTop-navheight;
  
        $('body,html').animate({
        scrollTop: totalScroll
        }, 300);
      }
    });
  
  })(window.jQuery);


