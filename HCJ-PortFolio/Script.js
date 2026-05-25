const nav = document.querySelector(".nav"),
      navList = nav.querySelectorAll("li"),
      totalNavList = navList.length,
      allSection = document.querySelectorAll(".section"),
      totalSection = allSection.length;
      for (let i = 0; i < totalNavList; i++) {
           const a = navList[i].querySelector("a");
           a.addEventListener("click", function() 
           {
            for(let i=0; i<totalSection; i++){
                allSection[i].classList.remove("back-section");
            }
            for(let j=0; j<totalNavList; j++)
            {
                if(navList[j].querySelector("a").classList.contains("active")){
                    allSection[j].classList.add("back-section");
                }
                navList[j].querySelector("a").classList.remove("active");
            }
            this.classList.add("active");
            showSection(this);
           })
    }
    function showSection(element){
        for(let i=0; i<totalSection; i++){
            allSection[i].classList.remove("active");
        }
        const target = element.getAttribute("href").split('#')[1];
        document.querySelector('#' + target).classList.add("active")
    }
    const navTogglerBtn = document.querySelector(".nav-toggler");
          aside = document.querySelector(".aside");
          navTogglerBtn.addEventListener("click", () =>
          {
              asideSectionTogglerBtn();
          })
          function asideSectionTogglerBtn(){
             aside.classList.toggle("open");
             navTogglerBtn.classList.toggle("open");
             for(let i=0; i<totalSection; i++){
                allSection[i].classList.toggle("open");
             }
          }

          /* Onclick Response */

          document.getElementById("GS_verify").onclick = function() {
            window.location.href = "https://www.coursera.org/account/accomplishments/professional-cert/QVPS6NCTJP0F";
          };

          document.getElementById("MetaSmm_verify").onclick = function() {
            window.location.href = "https://www.coursera.org/account/accomplishments/professional-cert/6M12LMR0SGWN";
          };

          document.getElementById("MetaDmm_verify").onclick = function() {
            window.location.href = "https://www.credly.com/badges/54769d64-1828-4a19-b7ac-fc281ed1f7c0/public_url";
          };

          document.getElementById("AWSCsa_verify").onclick = function() {
            window.location.href = "https://www.coursera.org/account/accomplishments/professional-cert/D1N2KD8HO0ZQ";
          };

          document.getElementById("AWSCp_verify").onclick = function() {
            window.location.href = "https://www.credly.com/badges/a7a355d2-9171-4ad8-bf62-9ebf5d14c868/public_url";
          };

          document.getElementById("MedMeta_verify").onclick = function() {
            window.location.href = "https://www.arkinx.com/profile/sakaethrambusiness/forum-posts";
          };

          document.getElementById("LinkedIn_connect").onclick = function() {
            window.location.href = "https://www.linkedin.com/in/r-sakaeth-ram-82614731b/";
          };

          document.getElementById("GitHub_connect").onclick = function() {
            window.location.href = "https://github.com/SakaethRam";
          };

          document.getElementById("Pro_verify").onclick = function() {
            window.location.href = "assets/Professional.pdf";
          };

          document.getElementById("Cert_verify").onclick = function() {
            window.location.href = "assets/Certification.pdf";
          };

          document.getElementById("CoverL_PDF").onclick = function() {
            window.location.href = "assets/Cover Letter.pdf";
          };

          document.getElementById("ResM_PDF").onclick = function() {
            window.location.href = "assets/Resume.pdf";
          };

          document.getElementById("OfferL_PDF").onclick = function() {
            window.location.href = "assets/Offer Letter.pdf";
          };

        window.addEventListener('load', function() {
          const splashScreen = document.getElementById('splash-screen');
          const mainContent = document.getElementById('main-content');
      
          setTimeout(function() {
              splashScreen.style.opacity = '0';
              splashScreen.style.transition = 'opacity 0.8s ease';
      
              // Hide splash screen after fade-out
              setTimeout(function() {
                  splashScreen.style.display = 'none';
                  mainContent.style.display = 'block';
              }, 500);
          }, 3000); // Display splash screen for 3 seconds
      });
      

        
